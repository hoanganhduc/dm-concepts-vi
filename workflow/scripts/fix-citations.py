#!/usr/bin/env python3
"""Apply the citation audit (workflow/loop/review/citation-issues.json):
  - page-mismatch: the term IS in the source but at a different page -> correct
    pdf_page to the found page nearest the cited one.
  - term-not-found: the term does not appear in the cited source -> downgrade the
    citation to an uncited usage (verified=false, no source/page); the term is
    kept. This guarantees every remaining verified citation is real.
"""
import glob
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    issues = json.load(open(os.path.join(ROOT, "workflow", "loop", "review", "citation-issues.json"),
                             encoding="utf-8"))
    by_id = defaultdict(list)
    for x in issues:
        by_id[x["id"]].append(x)

    fixed_page = downgraded = 0
    for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")):
        d = json.load(open(f, encoding="utf-8"))
        changed = False
        for e in d["final_entries"]:
            if e["id"] not in by_id:
                continue
            for t in e.get("vi_terms", []):
                for x in by_id[e["id"]]:
                    if not (t.get("verified") and t.get("term") == x["term"]
                            and t.get("source_id") == x["source"]):
                        continue
                    if x["problem"] == "page-mismatch" and x.get("found_pages"):
                        cited = x.get("cited_page") or 0
                        newp = min(x["found_pages"], key=lambda p: abs(p - cited))
                        t["pdf_page"] = newp
                        t["page"] = f"tr. {newp} (PDF)"
                        fixed_page += 1
                        changed = True
                    elif x["problem"] == "term-not-found":
                        t["verified"] = False
                        t["source_id"] = ""
                        t["page"] = ""
                        t["pdf_page"] = 0
                        t["snippet"] = ""
                        downgraded += 1
                        changed = True
        if changed:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"page-mismatch fixed: {fixed_page}; term-not-found downgraded: {downgraded}")


if __name__ == "__main__":
    main()
