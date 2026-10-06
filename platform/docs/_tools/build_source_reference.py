"""Build/check the documentation's static Python reference without importing runtime code.

Run from any directory: python3 docs/_tools/build_source_reference.py [--check].
Only MODULES.md, RESOURCES.md, the indexes and marked navigation blocks are generated.
Existing prose is preserved; missing README files get a package navigation page.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
ROOTS = ("src", "pl_gui", "tests", "scripts", "packaging")
RESOURCE_ROOTS = (*ROOTS, "config", "bootstrap")
BEGIN = "<!-- source-navigation:start -->"
END = "<!-- source-navigation:end -->"


def doc_dir(source: Path) -> Path:
    relative = source.relative_to(ROOT)
    if relative.parts[0] == "bootstrap":
        return DOCS / "environment_bootstrap" / Path(*relative.parts[1:])
    if relative.parts[0] == "src":
        relative = Path(*relative.parts[1:]) if len(relative.parts) > 1 else Path("source")
    return DOCS / relative


def link(origin: Path, target: Path) -> str:
    return Path(os.path.relpath(target, origin.parent)).as_posix()


def summary(node: ast.AST) -> str:
    value = ast.get_docstring(node) or ""
    return " ".join(value.split()).replace("|", "\\|")


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    result = f"{prefix} {node.name}({ast.unparse(node.args)})"
    if node.returns:
        result += " -> " + ast.unparse(node.returns)
    return result


def assignments(body: list[ast.stmt]) -> list[str]:
    results = []
    for node in body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if not node.target.id.startswith("_"):
                results.append(ast.unparse(node))
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if any(not n.startswith("_") or n == "__all__" for n in names):
                results.append(ast.unparse(node))
    return results


def render_module(path: Path, output: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    relative = path.relative_to(ROOT).as_posix()
    lines = [f"## `{path.name}`", "", f"Source: [{relative}]({link(output, path)}).", ""]
    if summary(tree):
        lines += [summary(tree), ""]
    imports = sorted({
        "." * node.level + (node.module or "")
        for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    } | {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names})
    if imports:
        lines += ["Imports (including optional/function-local imports; not a startup dependency list): "
                  + ", ".join(f"`{name}`" for name in imports) + ".", ""]
    if path.name == "__init__.py":
        exports = [ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        if exports:
            lines += ["Package-level import/export surface:", "", "```python", *exports, "```", ""]
    values = assignments(tree.body)
    if values:
        lines += ["Module declarations (expressions are shown without evaluating them):", "", "```python", *values, "```", ""]
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    for node in nodes:
        if isinstance(node, ast.ClassDef):
            lines += [f"### `{node.name}`", ""]
            bases = ", ".join([*(ast.unparse(base) for base in node.bases), *(ast.unparse(k) for k in node.keywords)])
            lines += ["```python", *("@" + ast.unparse(d) for d in node.decorator_list),
                      f"class {node.name}" + (f"({bases})" if bases else "") + ":", "```", ""]
            if summary(node):
                lines += [summary(node), ""]
            fields = assignments(node.body)
            if fields:
                lines += ["Declared fields/defaults:", "", "```python", *fields, "```", ""]
            methods = [m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and (not m.name.startswith("_") or m.name == "__init__")]
            if methods:
                lines += ["Directly declared public methods and constructor (inherited methods are documented on their base class):", ""]
                for method in methods:
                    decorators = ["@" + ast.unparse(d) for d in method.decorator_list]
                    lines += ["```python", *decorators, signature(method), "```", ""]
                    if summary(method):
                        lines += [summary(method), ""]
        else:
            lines += [f"### `{node.name}`", "", "```python", signature(node), "```", ""]
            if summary(node):
                lines += [summary(node), ""]
    if not nodes and not values:
        lines += ["No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.", ""]
    return "\n".join(lines)


def build() -> dict[Path, str]:
    groups: dict[Path, list[Path]] = defaultdict(list)
    for name in ROOTS:
        for path in sorted((ROOT / name).rglob("*.py")):
            if "__pycache__" not in path.parts:
                groups[path.parent].append(path)
    # Root utilities are part of the project, too.
    groups[ROOT] = sorted(ROOT.glob("*.py"))
    resources: dict[Path, list[Path]] = defaultdict(list)
    empty_directories = set()
    for name in RESOURCE_ROOTS:
        for path in sorted((ROOT / name).rglob("*")):
            if any(part in ("__pycache__", ".git") or part.endswith(".egg-info") for part in path.parts):
                continue
            if path.is_file() and path.suffix not in (".py", ".pyc"):
                resources[path.parent].append(path)
            elif path.is_dir() and not any(path.iterdir()):
                empty_directories.add(path)
    directories = set(groups) | set(resources) | empty_directories | {ROOT / name for name in RESOURCE_ROOTS if (ROOT / name).exists()}
    for source in list(directories):
        parent = source.parent
        while parent != ROOT and ROOT in parent.parents:
            directories.add(parent)
            parent = parent.parent
    outputs = {}
    resource_index = ["# Resource and data coverage", "",
                      "Generated inventory of non-Python files under source, GUI, tests, scripts, packaging, config and environment bootstrap. File contents are not copied: user accounts, machine settings, calibration captures and model data remain at their owning source/storage paths. Caches and generated egg-info are excluded.", "",
                      "Runtime snapshots and dated workpieces are data, not importable modules. Their directory pages establish ownership/file coverage without treating them as reusable APIs.", "",
                      "| Source directory | Resource reference | Files |", "|---|---|---:|"]
    index = ["# Python source coverage", "", "Generated with `python3 docs/_tools/build_source_reference.py`.", "",
             "Paths mirror the repository: `src/engine/x` maps to `docs/engine/x`; other roots keep their names.", "",
             "Every Python file is parsed without executing it, including vendor code, demos and tests. This is structural/API coverage, not proof of runtime correctness. Docstrings are source descriptions, not independently verified behavior. Private implementation details remain in the linked source. Data/assets and configuration are explained in the guides; generated caches, build outputs and environments are excluded.", "",
             "| Source directory | Documentation | Python files directly in directory |", "|---|---|---:|"]
    for source in sorted(directories):
        target = doc_dir(source) if source != ROOT else DOCS / "utilities"
        readme = target / "README.md"
        files = groups.get(source, [])
        if files:
            reference = target / "MODULES.md"
            outputs[reference] = "\n".join([
                f"# Module reference: `{source.relative_to(ROOT).as_posix()}`", "",
                f"[Package guide](README.md) · [Complete source index]({link(reference, DOCS / 'SOURCE_INDEX.md')})", "",
                "Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.", "",
                "## Files", "", *[f"- [{p.name}](#{p.name.replace('.', '').lower()})" for p in files], "",
                *[render_module(p, reference) for p in files],
            ]) + "\n"
        assets = resources.get(source, [])
        if assets:
            reference = target / "RESOURCES.md"
            lines = [f"# Resources: `{source.relative_to(ROOT).as_posix()}`", "",
                     "[Directory guide](README.md). This inventory records paths and formats; it does not publish stored values or certify their suitability for another machine.", "",
                     "| File | Format |", "|---|---|"]
            for asset in assets:
                lines.append(f"| [{asset.name}]({link(reference, asset)}) | `{asset.suffix.lstrip('.') or 'extensionless'}` |")
            outputs[reference] = "\n".join(lines) + "\n"
            resource_index.append(f"| `{source.relative_to(ROOT).as_posix()}` | [Resources]({link(DOCS / 'RESOURCE_INDEX.md', reference)}) | {len(assets)} |")
        children = sorted(p for p in directories if p.parent == source and p != source)
        navigation = [BEGIN, "## Source navigation", ""]
        if files:
            navigation += ["[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.", ""]
        if assets:
            navigation += ["[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.", ""]
        if children:
            navigation += ["| Source subdirectory | Guide |", "|---|---|"]
            for child in children:
                navigation.append(f"| `{child.name}/` | [{child.name}]({link(readme, doc_dir(child) / 'README.md')}) |")
            navigation.append("")
        navigation += [f"[Complete source index]({link(readme, DOCS / 'SOURCE_INDEX.md')}).", END]
        if readme.exists():
            content = readme.read_text()
            if BEGIN in content:
                content = content[:content.index(BEGIN)].rstrip() + "\n\n"
            else:
                content = content.rstrip() + "\n\n"
        else:
            label = source.relative_to(ROOT).as_posix()
            content = f"# `{label}`\n\n"
            if source.name in ("controller", "model", "view", "service") and "applications" in source.parts:
                meanings = {"controller": "Coordinates model/view actions and owns subscriptions and UI worker lifetimes.",
                            "model": "Maintains screen state and delegates queries/commands to the injected service.",
                            "view": "Qt widgets, user-action signals and data setters for the owning application.",
                            "service": "Application service contract, runtime adapters and available development stubs."}
                content += meanings[source.name] + "\n\n"
            elif "storage" in source.parts:
                content += "System-owned persistent data, defaults, calibration artifacts or catalogs. Resolve this directory through the owning system's storage helpers; installed writable data may be relocated by `ROBOT_PLATFORM_DATA_ROOT`. Shared implementation does not make these files interchangeable between machines/profiles.\n\n"
            elif source.name == "localization":
                content += "Application-owned translation catalogs/resources. Shared startup loads application catalogs before robot-system overrides. Preserve Qt context/source keys across languages; verify initial translation and runtime language switching.\n\n"
            elif source.name == "resources":
                content += "Bundled presentation assets. Consumers resolve these paths through their owning package; include the assets when packaging the application/framework.\n\n"
            elif source in empty_directories:
                content += "This source directory is empty in the checkout. It supplies no implemented Python API or checked-in resource files.\n\n"
            else:
                content += "This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.\n\n"
            if source.parent in directories and source != ROOT:
                parent_readme = doc_dir(source.parent) / "README.md" if source.parent != ROOT else DOCS / "README.md"
                content += f"[Parent guide]({link(readme, parent_readme)}).\n\n"
        outputs[readme] = content + "\n".join(navigation) + "\n"
        index.append(f"| `{source.relative_to(ROOT).as_posix()}` | [Guide]({link(DOCS / 'SOURCE_INDEX.md', readme)}) | {len(files)} |")
    outputs[DOCS / "SOURCE_INDEX.md"] = "\n".join(index) + f"\n\nTotal: {sum(map(len, groups.values()))} Python files in {len(directories)} source directories.\n"
    outputs[DOCS / "RESOURCE_INDEX.md"] = "\n".join(resource_index) + f"\n\nTotal: {sum(map(len, resources.values()))} resource files in {len(resources)} directories.\n"
    return {path: content.rstrip() + "\n" for path, content in outputs.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on missing/stale generated references or navigation")
    args = parser.parse_args()
    outputs = build()
    stale = []
    for path, content in outputs.items():
        if path.exists() and path.read_text() == content:
            continue
        if args.check:
            stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        print("Missing/stale documentation:\n" + "\n".join(stale))
        return 1
    print(f"{'Checked' if args.check else 'Updated'} {len(outputs)} documentation files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
