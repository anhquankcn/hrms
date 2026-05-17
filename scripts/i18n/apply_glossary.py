#!/usr/bin/env python3
"""
Apply Vietnamese accounting/finance glossary to Frappe + ERPNext + HRMS translation files.

Strategy:
  1. For msgid that EXACTLY matches an English key in glossary -> set msgstr to standard Vietnamese.
  2. For msgstr containing 'alt' (wrong/old) Vietnamese forms -> replace with standard form (word boundary).
  3. Pronoun replacements (Quy khach -> ban).

Usage:
  python3 apply_glossary.py [--dry-run]
"""
import json
import re
import sys
import csv
import shutil
from pathlib import Path

GLOSSARY = Path(__file__).parent / "glossary.json"

FRAPPE_PO = Path("/Users/quanna/frappe-bench/apps/frappe/frappe/locale/vi.po")
HRMS_PO = Path("/Users/quanna/Sources/hrms/hrms/locale/vi.po")
ERPNEXT_CSV = Path("/Users/quanna/frappe-bench/apps/erpnext/erpnext/translations/vi.csv")

DRY_RUN = "--dry-run" in sys.argv


def load_glossary():
    data = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    exact = {}
    alt_map = {}
    for category, entries in data.items():
        if category.startswith("_"):
            continue
        if category == "pronouns_casual":
            for wrong, right in entries.items():
                alt_map[wrong] = right
            continue
        for en, info in entries.items():
            if not isinstance(info, dict):
                continue
            vi = info["vi"]
            exact[en] = vi
            for alt in info.get("alt", []):
                if alt and alt != vi:
                    alt_map[alt] = vi
    return exact, alt_map


def apply_alt_map(text, alt_map):
    """Word-boundary replacement of wrong Vietnamese forms."""
    if not text:
        return text
    for wrong, right in alt_map.items():
        pattern = r"\b" + re.escape(wrong) + r"\b"
        text = re.sub(pattern, right, text)
    return text


def process_po(path, exact, alt_map):
    if not path.exists():
        print(f"  SKIP (not found): {path}")
        return 0, 0
    backup = path.with_suffix(path.suffix + ".pre-glossary.bak")
    if not DRY_RUN and not backup.exists():
        shutil.copy2(path, backup)

    content = path.read_text(encoding="utf-8")
    blocks = re.split(r"(\n\n)", content)

    msgid_re = re.compile(r'msgid "((?:[^"\\]|\\.)*)"')
    msgstr_re = re.compile(r'msgstr "((?:[^"\\]|\\.)*)"')

    exact_hits = 0
    alt_hits = 0
    out_blocks = []

    for block in blocks:
        if not block.strip() or block == "\n\n":
            out_blocks.append(block)
            continue
        mid = msgid_re.search(block)
        mst = msgstr_re.search(block)
        if not mid or not mst:
            out_blocks.append(block)
            continue
        msgid = mid.group(1)
        old_msgstr = mst.group(1)
        new_msgstr = old_msgstr

        if msgid in exact:
            target = exact[msgid]
            if new_msgstr != target:
                new_msgstr = target
                exact_hits += 1

        if alt_map and new_msgstr:
            replaced = apply_alt_map(new_msgstr, alt_map)
            if replaced != new_msgstr:
                alt_hits += 1
                new_msgstr = replaced

        if new_msgstr != old_msgstr:
            new_msgstr_line = f'msgstr "{new_msgstr}"'
            block = msgstr_re.sub(new_msgstr_line, block, count=1)

        out_blocks.append(block)

    if not DRY_RUN:
        path.write_text("".join(out_blocks), encoding="utf-8")
    return exact_hits, alt_hits


def process_csv(path, exact, alt_map):
    if not path.exists():
        print(f"  SKIP (not found): {path}")
        return 0, 0
    backup = path.with_suffix(".csv.pre-glossary.bak")
    if not DRY_RUN and not backup.exists():
        shutil.copy2(path, backup)

    exact_hits = 0
    alt_hits = 0
    rows_out = []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                rows_out.append(row)
                continue
            en = row[0] if len(row) > 0 else ""
            vi = row[1] if len(row) > 1 else ""
            old_vi = vi

            if en in exact:
                target = exact[en]
                if vi != target:
                    vi = target
                    exact_hits += 1

            if vi:
                replaced = apply_alt_map(vi, alt_map)
                if replaced != vi:
                    alt_hits += 1
                    vi = replaced

            if vi != old_vi:
                if len(row) > 1:
                    row[1] = vi
                else:
                    row.append(vi)
            rows_out.append(row)

    if not DRY_RUN:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(rows_out)

    return exact_hits, alt_hits


def main():
    exact, alt_map = load_glossary()
    print(f"Glossary loaded: {len(exact)} exact terms, {len(alt_map)} alt mappings")
    print(f"Dry-run: {DRY_RUN}\n")

    for label, path, fn in [
        ("Frappe (.po)", FRAPPE_PO, process_po),
        ("HRMS (.po)", HRMS_PO, process_po),
        ("ERPNext (.csv)", ERPNEXT_CSV, process_csv),
    ]:
        print(f"--- {label}: {path}")
        e, a = fn(path, exact, alt_map)
        print(f"  exact-set: {e}  alt-replaced: {a}\n")

    print("Done." + ("  (dry-run, no changes written)" if DRY_RUN else ""))


if __name__ == "__main__":
    main()
