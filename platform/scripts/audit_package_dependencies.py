"""Report static imports between proposed packages without importing application code."""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = {
    "src.shared_contracts": "contracts",
    "src.engine": "engine",
    "src.applications": "applications",
    "src.bootstrap": "bootstrap",
    "pl_gui": "shell",
}


def owner(module: str) -> str | None:
    """Map an import namespace to its proposed distribution boundary."""
    for prefix, package in SHARED.items():
        if module == prefix or module.startswith(prefix + "."):
            return package
    if module.startswith("src.robot_systems."):
        member = module.split(".")[2]
        if (ROOT / "src/robot_systems" / member).is_dir():
            return "system:" + member
        return "system-runtime"
    if module == "src.robot_systems":
        return "system-runtime"
    return None


def audit() -> dict:
    """Collect import sites, including relative imports and imports in guarded code."""
    edges = []
    external = Counter()
    counts = Counter()
    for directory in (ROOT / "src", ROOT / "pl_gui"):
        for path in sorted(directory.rglob("*.py")):
            relative = path.relative_to(ROOT)
            module_parts = list(relative.with_suffix("").parts)
            if module_parts[-1] == "__init__":
                module_parts.pop()
                package_parts = module_parts
            else:
                package_parts = module_parts[:-1]
            source = owner(".".join(module_parts))
            if source is None:
                continue
            counts[source] += 1
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                imports = []
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    prefix = node.module or ""
                    if node.level:
                        base = package_parts[:len(package_parts) - node.level + 1]
                        prefix = ".".join(base + ([prefix] if prefix else []))
                    imports = [prefix + "." + alias.name for alias in node.names]
                for imported in imports:
                    target = owner(imported)
                    if target and target != source:
                        edges.append({"source": source, "target": target,
                                      "file": relative.as_posix(), "line": node.lineno,
                                      "import": imported})
                    elif target is None:
                        external[(source, imported.split(".")[0])] += 1
    return {"files": dict(sorted(counts.items())),
            "edges": sorted(edges, key=lambda item: (item["source"], item["target"], item["file"], item["line"])),
            "external_import_roots": [{"package": package, "module": module, "sites": count}
                                      for (package, module), count in sorted(external.items())]}


def markdown(report: dict) -> str:
    """Render an overview and representative import sites for every dependency."""
    lines = ["# Package dependency audit", "",
             "Generated with `python scripts/audit_package_dependencies.py`. Regenerate after boundary changes.", "",
             "Static AST scan of `src/` and `pl_gui/`: includes demos, nested imports, fallback imports and TYPE_CHECKING blocks. Counts are import sites, not runtime dependencies. Dynamic import strings, resources, ROS/native dependencies and dependency versions require manual review. External roots include stdlib and unresolved legacy namespaces; they are not a pip requirements list.", "",
             "## Python files", "", "| Proposed package | Files |", "|---|---:|"]
    lines.extend(f"| {name} | {count} |" for name, count in report["files"].items())
    grouped = {}
    for edge in report["edges"]:
        grouped.setdefault((edge["source"], edge["target"]), []).append(edge)
    lines += ["", "## Dependencies", "", "| Importing package | Imported package | Import sites |", "|---|---|---:|"]
    lines.extend(f"| {source} | {target} | {len(edges)} |" for (source, target), edges in grouped.items())
    lines += ["", "## Representative evidence", ""]
    for (source, target), edges in grouped.items():
        lines += [f"### {source} → {target}", ""]
        lines.extend(f"- `{edge['file']}:{edge['line']}` → `{edge['import']}`" for edge in edges[:5])
        if len(edges) > 5:
            lines.append(f"- {len(edges) - 5} additional import sites; use `--json` for the complete list.")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Output all evidence as JSON")
    options = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2) if options.json else markdown(report))
