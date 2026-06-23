#!/usr/bin/env python3
"""Apply one loop's Codex web-review findings (workflow/loop/review/findings-<i>.json).

Per the editorial policy (keep the book's recommended term; add alternatives as
variants): every Codex-found missing translation and every "better term" from an
uncommon-verdict is added as an uncited usage variant (verified=false,
recommended=false) if not already present. Uncommon verdicts are logged for the
editor. Non-destructive; recommended terms are never changed.

Usage: apply-review.py <loop-number>
"""
import glob
import json
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REVIEW = os.path.join(ROOT, "workflow", "loop", "review")


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "d").lower().strip()


def variant(term):
    return {"term": term, "source_id": "", "page": "", "pdf_page": 0, "snippet": "",
            "verified": False, "recommended": False}


def main():
    i = sys.argv[1]
    data = json.load(open(os.path.join(REVIEW, f"findings-{i}.json"), encoding="utf-8"))
    findings = {x["id"]: x for x in data.get("findings", [])}
    files, idmap = {}, {}
    for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")):
        d = json.load(open(f, encoding="utf-8"))
        files[f] = d
        for e in d["final_entries"]:
            idmap[e["id"]] = e

    added, flagged = 0, []
    for eid, fd in findings.items():
        e = idmap.get(eid)
        if not e or e.get("see_ref"):
            continue
        have = {norm(t.get("term", "")) for t in e.get("vi_terms", [])}
        for mv in (fd.get("missing_variants") or []):
            term = (mv.get("term") or "").strip()
            if term and norm(term) not in have:
                e["vi_terms"].append(variant(term))
                have.add(norm(term))
                added += 1
        com = fd.get("commonality") or {}
        if com.get("verdict") == "uncommon":
            bt = (com.get("better_term") or "").strip()
            if bt and norm(bt) not in have:
                e["vi_terms"].append(variant(bt))
                have.add(norm(bt))
                added += 1
            flagged.append({"id": eid, "better_term": bt, "source": com.get("source", "")})

    for f, d in files.items():
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(REVIEW, "review-log.jsonl"), "a", encoding="utf-8").write(
        json.dumps({"loop": i, "variants_added": added, "uncommon_flagged": flagged},
                   ensure_ascii=False) + "\n")
    print(f"loop {i}: added {added} variant(s); flagged {len(flagged)} uncommon-recommended for editor")


if __name__ == "__main__":
    main()
