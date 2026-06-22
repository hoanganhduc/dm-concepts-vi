#!/usr/bin/env python3
"""Apply data/synonym-groups.json: for each group, merge each secondary entry's
distinct Vietnamese terms into the canonical entry (as variants), then replace
the secondary with a 'see' cross-reference stub pointing to the canonical.

Keeps both headwords findable; the concept is defined once (canonical) and the
synonym links to it. Edits workflow/panels/chapter-*-final.json in place.
"""
import glob
import json
import os
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "d").lower().strip()


def main():
    groups = json.load(open(os.path.join(ROOT, "data", "synonym-groups.json"), encoding="utf-8"))
    files = {f: json.load(open(f, encoding="utf-8"))
             for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json"))}
    idmap = {}
    for f, d in files.items():
        for e in d["final_entries"]:
            idmap[e["id"]] = (f, e)

    stubs = merged = 0
    for g in groups:
        cid = g.get("canonical")
        if cid not in idmap:
            continue
        _, ce = idmap[cid]
        canon = {norm(t["term"]) for t in ce.get("vi_terms", [])}
        for sid in g.get("secondaries", []):
            if sid not in idmap:
                continue
            sf, se = idmap[sid]
            if se.get("see_ref"):
                continue  # already a stub
            # merge secondary's distinct VI terms into the canonical as variants
            for t in se.get("vi_terms", []):
                if t.get("term") and norm(t["term"]) not in canon:
                    nt = dict(t)
                    nt["recommended"] = False
                    ce["vi_terms"].append(nt)
                    canon.add(norm(t["term"]))
                    merged += 1
            # distinct secondary terms (for the stub's index/display)
            seen, terms = set(), []
            for t in se.get("vi_terms", []):
                if t.get("term") and norm(t["term"]) not in seen:
                    seen.add(norm(t["term"]))
                    terms.append({"term": t["term"], "verified": False, "recommended": False,
                                  "source_id": "", "page": "", "pdf_page": 0, "snippet": ""})
            stub = {"id": se["id"], "letter": se["letter"], "headword_en": se["headword_en"],
                    "see_ref": cid, "vi_terms": terms, "see_also": [],
                    "notes": f"Đồng nghĩa với {ce['headword_en']}."}
            d = files[sf]
            d["final_entries"] = [stub if x["id"] == sid else x for x in d["final_entries"]]
            idmap[sid] = (sf, stub)
            stubs += 1

    for f, d in files.items():
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"created {stubs} see-stubs; merged {merged} VI variant(s) into canonicals.")


if __name__ == "__main__":
    main()
