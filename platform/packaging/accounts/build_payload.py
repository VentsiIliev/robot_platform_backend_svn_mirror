#!/usr/bin/env python3
"""Build a stdlib-only Manufacturer maintenance archive; no GUI or credentials."""
import argparse
import ast
import hashlib
from importlib.util import resolve_name
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ENTRY = "src.bootstrap.account_maintenance"
ALLOWED = (ENTRY, "src.engine.auth.", "src.shared_contracts.accounts.",
           "src.shared_contracts.authorization.")


def maintenance_sources(root=ROOT):
    pending, sources = [ENTRY], {}
    while pending:
        module = pending.pop()
        if module in sources:
            continue
        if not any(module == prefix or module.startswith(prefix) for prefix in ALLOWED):
            raise ValueError(f"Unexpected maintenance dependency: {module}")
        path = root.joinpath(*module.split(".")).with_suffix(".py")
        source = path.read_bytes()
        sources[module] = source
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                if node.level:
                    package = module.rpartition(".")[0]
                    base = resolve_name("." * node.level + (node.module or ""), package)
                    imports = [base] if node.module else [base + "." + alias.name for alias in node.names]
                else:
                    imports = [node.module]
            elif isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            else:
                continue
            for imported in imports:
                if imported.startswith("src."):
                    pending.append(imported)
                elif imported.split(".")[0] not in sys.stdlib_module_names:
                    raise ValueError(f"Non-stdlib maintenance dependency: {imported}")
    return sources


def build_payload(destination, root=ROOT):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    modules = maintenance_sources(root)
    archive = destination / "account-maintenance.pyz"
    entries = {name.replace(".", "/") + ".py": source for name, source in modules.items()}
    for name in modules:
        parts = name.split(".")[:-1]
        for depth in range(1, len(parts) + 1):
            # This isolated tool deliberately has no application package imports.
            entries["/".join(parts[:depth]) + "/__init__.py"] = b""
    entries["__main__.py"] = b"from src.bootstrap.account_maintenance import main\nraise SystemExit(main())\n"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for name, source in sorted(entries.items()):
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100444 << 16
            output.writestr(info, source)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / "account-maintenance.pyz.sha256").write_text(digest + "  account-maintenance.pyz\n")
    shutil.copy2(root / "packaging/accounts/install.py", destination / "install.py")
    shutil.copy2(root / "packaging/accounts/README.md", destination / "README.md")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(build_payload(parser.parse_args().destination))


if __name__ == "__main__":
    main()
