#!/usr/bin/env python3
"""Validate Blind Spot Atlas entries.

Checks every file in _blindspots/:
  1. Frontmatter parses as YAML and validates against schema/blindspot.schema.json
  2. `id` matches the filename
  3. The body contains the five fixed sections, in order:
       ## The failure / ## Why it happens / ## Detection / ## Mitigation / ## Status
  4. The body contains a repro block: a "### Minimal repro" heading,
     a fenced code block, and a dated "**Last checked:**" line.

Exit code 0 = all entries valid. Nonzero = failures (printed per file).

Usage: python3 scripts/validate_entries.py
Deps:  pip install pyyaml jsonschema
"""

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = ROOT / "_blindspots"
SCHEMA_PATH = ROOT / "schema" / "blindspot.schema.json"

REQUIRED_SECTIONS = [
    "## The failure",
    "## Why it happens",
    "## Detection",
    "## Mitigation",
    "## Status",
]

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
LAST_CHECKED_RE = re.compile(r"\*\*Last checked:\*\*\s*\d{4}-\d{2}-\d{2}")
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)


def validate_entry(path: Path, validator: Draft202012Validator) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    m = FRONTMATTER_RE.match(text)
    if not m:
        return ["missing or malformed frontmatter block (--- ... ---)"]

    raw_fm, body = m.group(1), m.group(2)

    try:
        fm = yaml.safe_load(raw_fm)
    except yaml.YAMLError as e:
        return [f"frontmatter is not valid YAML: {e}"]

    if not isinstance(fm, dict):
        return ["frontmatter did not parse to a mapping"]

    # YAML parses unquoted dates to datetime.date; schema wants strings.
    for key in ("added", "last-reviewed"):
        if key in fm and not isinstance(fm[key], str):
            fm[key] = str(fm[key])

    for err in sorted(validator.iter_errors(fm), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"frontmatter {loc}: {err.message}")

    if fm.get("id") != path.stem:
        errors.append(f"id '{fm.get('id')}' does not match filename '{path.stem}'")

    # Five fixed sections, in order.
    positions = []
    for section in REQUIRED_SECTIONS:
        idx = body.find(section + "\n")
        if idx == -1:
            idx = body.find(section)
        if idx == -1:
            errors.append(f"missing required section: '{section}'")
        positions.append(idx)
    found = [p for p in positions if p != -1]
    if found != sorted(found):
        errors.append("required sections are out of order")

    # Repro requirement — the whole epistemics of the atlas.
    if "### Minimal repro" not in body:
        errors.append("missing '### Minimal repro' block (entries without a repro belong in drafts/)")
    if not CODE_FENCE_RE.search(body):
        errors.append("repro must include a fenced code block with the exact prompt")
    if not LAST_CHECKED_RE.search(body):
        errors.append("repro must include a dated '**Last checked:** YYYY-MM-DD' line")

    return errors


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    entry_files = sorted(ENTRIES_DIR.glob("*.md"))
    if not entry_files:
        print("No entries found in _blindspots/ — nothing to validate.")
        return 1

    failed = 0
    for path in entry_files:
        errors = validate_entry(path, validator)
        if errors:
            failed += 1
            print(f"FAIL {path.relative_to(ROOT)}")
            for e in errors:
                print(f"     - {e}")
        else:
            print(f"ok   {path.relative_to(ROOT)}")

    print(f"\n{len(entry_files) - failed}/{len(entry_files)} entries valid.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
