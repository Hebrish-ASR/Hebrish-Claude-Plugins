#!/usr/bin/env python3
"""Add reviewed sentence rows (JSONL) to a contribution file, or start a new contribution file.

  python3 assemble.py new <name> --contributor <github-handle> > <name>.json   # empty skeleton
  python3 assemble.py add <name>.json rows.reviewed.jsonl [more.jsonl ...]   # append rows in place

`add` skips rows whose text is already in the file (case and punctuation ignored) and prints
how many it added. Rows must already carry `review` (see the write-sentences skill). Stdlib only.
"""
import argparse, datetime, json, re, sys
from pathlib import Path


def key(text):
    return " ".join(re.sub(r"[^\w\s]", "", text.lower()).split())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("name"); n.add_argument("--contributor", required=True)
    d = sub.add_parser("add"); d.add_argument("file"); d.add_argument("rows", nargs="+")
    a = ap.parse_args()
    if a.cmd == "new":
        print(json.dumps({"format": "hebrish-contribution/1", "name": a.name, "created": datetime.date.today().isoformat(),
                          "contributor": a.contributor, "licence": "CC-BY-4.0", "note": "", "companions": {},
                          "terms": [], "sentences": []}, ensure_ascii=False, indent=1))
        return
    path = Path(a.file)
    doc = json.loads(path.read_text(encoding="utf-8"))
    have = {key(s["text"]) for s in doc.setdefault("sentences", [])}
    added = 0
    for f in a.rows:
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if key(row["text"]) in have:
                continue
            have.add(key(row["text"]))
            doc["sentences"].append(row)
            added += 1
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{added} rows added; {len(doc['sentences'])} sentences in {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
