#!/usr/bin/env python3
"""Insert the publisher into each <biblio> in source/references.ptx, using
data/publishers.json (biblio_id -> {publisher, ...}). Inserts the publisher
right before the year: '... <em>Title</em>. <Publisher>, YYYY.'.
Entries with no publisher are left unchanged.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REFS = os.path.join(ROOT, "source", "references.ptx")


def main():
    pubs = json.load(open(os.path.join(ROOT, "data", "publishers.json"), encoding="utf-8"))
    lines = open(REFS, encoding="utf-8").read().splitlines(keepends=True)
    out, changed = [], 0
    for line in lines:
        m = re.search(r'xml:id="(bib-[a-z0-9-]+)"', line)
        if m and m.group(1) in pubs:
            pub = (pubs[m.group(1)] or {}).get("publisher", "").strip()
            if pub and pub.lower() not in ("", "none / unknown", "unknown") and "NXB" in pub or (pub and pub.startswith("NXB")):
                # insert publisher before the trailing "YYYY.</biblio>"
                new = re.sub(r"(\d{4})\.(</biblio>)", rf"{pub}, \1.\2", line, count=1)
                if new != line:
                    line = new
                    changed += 1
        out.append(line)
    open(REFS, "w", encoding="utf-8").write("".join(out))
    print(f"updated {changed} biblio entries with publisher")


if __name__ == "__main__":
    main()
