#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
]

# Construct selected internal markers without embedding them verbatim in this checker.
FORBIDDEN_INTERNAL_MARKERS = [
    "LIFE" + "-140",
    "@" + "gmail.com",
]

TEXT_EXTENSIONS = {
    ".md", ".py", ".ps1", ".json", ".yaml", ".yml", ".txt", ".example"
}

def main():
    failures = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.resolve() == SELF:
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        if p.suffix.lower() not in TEXT_EXTENSIONS and p.name not in {".gitignore", ".env.example"}:
            continue

        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible API secret in {p.relative_to(ROOT)}")

        for marker in FORBIDDEN_INTERNAL_MARKERS:
            if marker.lower() in text.lower():
                failures.append(f"internal/private marker detected in {p.relative_to(ROOT)}")

    if failures:
        print("Public safety check: FAIL")
        for f in failures:
            print("-", f)
        return 1

    print("Public safety check: PASS")
    print("No API-key-shaped secret or selected internal markers found.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
