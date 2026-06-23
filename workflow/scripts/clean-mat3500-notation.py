#!/usr/bin/env python3
"""Two cleanups across chapter-*-final.json:

1. Drop MAT3500 citations: remove every vi_term whose source_id == bib-mat3500.
   The course term is KEPT as an (uncited) usage: if the same term is still
   attested by a corpus source, promote that row to recommended; otherwise keep
   the term as a recommended verified=false / no-citation row. bib-mat3500 is
   thereby no longer cited anywhere.

2. Fix garbled notation: a notation field containing Vietnamese letters is prose
   that was wrongly placed in math mode (renders as garbage in the symbol list);
   clear it so the entry drops out of the notation list.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAT = "bib-mat3500"
VIET = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]")


def main():
    cleared_notation = dropped = promoted = uncited = 0
    for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")):
        d = json.load(open(f, encoding="utf-8"))
        for e in d["final_entries"]:
            if e.get("notation") and VIET.search(e["notation"]):
                e["notation"] = ""
                cleared_notation += 1

            vts = e.get("vi_terms", [])
            mat_rows = [t for t in vts if t.get("source_id") == MAT]
            if not mat_rows:
                continue
            rec_terms = [t["term"] for t in mat_rows if t.get("recommended")]
            kept = [t for t in vts if t.get("source_id") != MAT]
            dropped += len(mat_rows)
            for term in rec_terms:
                already = [t for t in kept if t.get("term") == term]
                if any(t.get("recommended") for t in kept):
                    continue
                if already:
                    already[0]["recommended"] = True  # promote a corpus row
                    promoted += 1
                else:
                    kept.append({"term": term, "source_id": "", "page": "", "pdf_page": 0,
                                 "snippet": "", "verified": False, "recommended": True})
                    uncited += 1
            # ensure exactly one recommended survives
            recs = [t for t in kept if t.get("recommended")]
            for t in recs[1:]:
                t["recommended"] = False
            if not recs and kept:
                kept[0]["recommended"] = True
            e["vi_terms"] = kept
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"notation cleared: {cleared_notation}")
    print(f"mat3500 rows dropped: {dropped} (promoted corpus->recommended: {promoted}; "
          f"kept as uncited usage: {uncited})")


if __name__ == "__main__":
    main()
