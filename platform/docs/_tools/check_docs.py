"""Check documentation links, Markdown anchors, JSON syntax and source coverage.

Uses only the standard library, never imports production modules, and never
follows external links. Run: python3 docs/_tools/check_docs.py
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from build_source_reference import DOCS, ROOT, build


def without_fences(text: str) -> str:
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    counts = Counter()
    result = set()
    for title in re.findall(r"^#{1,6}\s+(.+)$", without_fences(text), flags=re.M):
        title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", title)
        slug = re.sub(r"[^\w\-\s]", "", title.lower()).replace(" ", "-")
        number = counts[slug]
        result.add(slug if number == 0 else f"{slug}-{number}")
        counts[slug] += 1
    result.update(re.findall(r'<(?:a|h[1-6])\s+[^>]*id=["\']([^"\']+)', text))
    return result


def main() -> int:
    errors = []
    link_count = 0
    pages = sorted(DOCS.rglob("*.md"))
    anchor_cache = {}
    for page in pages:
        for raw in re.findall(r"\]\(([^)\n]+)\)", without_fences(page.read_text())):
            value = raw.strip().strip("<>")
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                continue
            path = re.sub(r":\d+$", "", unquote(parsed.path))
            target = (page.parent / path).resolve() if path else page.resolve()
            link_count += 1
            if path.startswith("/"):
                errors.append(f"{page.relative_to(ROOT)}: nonportable absolute link {raw}")
            if not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: missing link target {raw}")
                continue
            # Historical source-line fragments and proposed-path discussions do
            # not establish current anchors; real Markdown links still must work.
            if parsed.fragment and target.suffix.lower() == ".md":
                if target not in anchor_cache:
                    anchor_cache[target] = anchors(target.read_text())
                if unquote(parsed.fragment) not in anchor_cache[target]:
                    errors.append(f"{page.relative_to(ROOT)}: missing Markdown anchor {raw}")
    for path, expected in build().items():
        if not path.exists() or path.read_text() != expected:
            errors.append(f"{path.relative_to(ROOT)}: missing/stale source reference or navigation")
    # Catalogs and checked-in configuration must remain parseable. Read only;
    # semantic validation and migration belong to the owning runtime service.
    json_files = sorted((ROOT / "src").rglob("*.json")) + sorted((ROOT / "config").rglob("*.json"))
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except (UnicodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
    if errors:
        print("\n".join(errors))
        print(f"Found {len(errors)} documentation/data validation errors.")
        return 1
    print(f"Validated {len(pages)} Markdown pages, {link_count} local links, {len(json_files)} JSON files and complete generated source coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
