#!/usr/bin/env python3
"""
Apply accounting-specific Vietnamese phrase translations to vi.po + vi.csv.
Only exact-match (full msgid -> msgstr). Run AFTER apply_glossary.py.
"""
import json
import re
import sys
import csv
import shutil
from pathlib import Path

GLOSSARY = Path(__file__).parent / "glossary_accounting.json"
FRAPPE_PO = Path("/Users/quanna/frappe-bench/apps/frappe/frappe/locale/vi.po")
HRMS_PO = Path("/Users/quanna/Sources/hrms/hrms/locale/vi.po")
ERPNEXT_CSV = Path("/Users/quanna/frappe-bench/apps/erpnext/erpnext/translations/vi.csv")

DRY_RUN = "--dry-run" in sys.argv


def load_phrases():
    data = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    out = {}
    for cat, entries in data.items():
        if cat.startswith("_"):
            continue
        for en, vi in entries.items():
            out[en] = vi
    return out


def process_po(path, phrases):
    if not path.exists():
        return 0
    backup = path.with_suffix(path.suffix + ".pre-accounting.bak")
    if not DRY_RUN and not backup.exists():
        shutil.copy2(path, backup)
    content = path.read_text(encoding="utf-8")
    msgid_re = re.compile(r'msgid "((?:[^"\\]|\\.)*)"')
    msgstr_re = re.compile(r'msgstr "((?:[^"\\]|\\.)*)"')
    blocks = re.split(r"(\n\n)", content)
    hits = 0
    out = []
    for b in blocks:
        if not b.strip() or b == "\n\n":
            out.append(b); continue
        mid = msgid_re.search(b)
        mst = msgstr_re.search(b)
        if not mid or not mst:
            out.append(b); continue
        msgid = mid.group(1)
        if msgid in phrases:
            target = phrases[msgid]
            if mst.group(1) != target:
                b = msgstr_re.sub(f'msgstr "{target}"', b, count=1)
                hits += 1
        out.append(b)
    if not DRY_RUN:
        path.write_text("".join(out), encoding="utf-8")
    return hits


def process_csv(path, phrases):
    if not path.exists():
        return 0
    backup = path.with_suffix(".csv.pre-accounting.bak")
    if not DRY_RUN and not backup.exists():
        shutil.copy2(path, backup)
    hits = 0
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if not row:
                rows.append(row); continue
            en = row[0]
            if en in phrases:
                target = phrases[en]
                if len(row) > 1:
                    if row[1] != target:
                        row[1] = target; hits += 1
                else:
                    row.append(target); hits += 1
            rows.append(row)
    if not DRY_RUN:
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f, quoting=csv.QUOTE_MINIMAL).writerows(rows)
    return hits


def main():
    phrases = load_phrases()
    print(f"Loaded {len(phrases)} accounting phrases. Dry-run: {DRY_RUN}\n")
    for label, p, fn in [
        ("Frappe (.po)", FRAPPE_PO, process_po),
        ("HRMS (.po)", HRMS_PO, process_po),
        ("ERPNext (.csv)", ERPNEXT_CSV, process_csv),
    ]:
        h = fn(p, phrases)
        print(f"  {label}: {h} phrases updated")


if __name__ == "__main__":
    main()
