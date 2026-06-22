#!/usr/bin/env python3
"""Add MAT3500 course terms as uncited usable variants (recommended unchanged).

Per the editorial decision: keep the book's recommended term, add the course's
Vietnamese term as a vi_term variant with no citation (verified=false,
recommended=false, empty source/page) — rendered as "biến thể, chưa có trích dẫn
cụ thể". Only the Group-A terms (course term not already a book variant) need it;
Group-B course terms are already listed variants.
"""
import glob
import json
import os
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (english headword, cleaned course Vietnamese term to add as a variant)
PAIRS = [
    ("ancestors", "đỉnh tổ tiên"),
    ("karnaugh maps", "sơ đồ Karnaugh"),
    ("knight's tour", "đường đi tuần của quân mã"),
    ("least common multiple", "bội chung nhỏ nhất"),
    ("maximum matching", "ghép cặp cực đại"),
    ("neighborhood", "tập láng giềng"),
    ("one-to-one function", "hàm một-một"),
    ("ordered pair", "cặp sắp thứ tự"),
    ("perfect matching", "ghép cặp hoàn hảo"),
    ("regular graph", "đồ thị chính quy"),
]


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "d").lower().strip()


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")))
    docs = {f: json.load(open(f, encoding="utf-8")) for f in files}
    index = {}
    for f, d in docs.items():
        for e in d.get("final_entries", []):
            index[e["headword_en"].lower()] = (f, e)

    added, touched = 0, set()
    for en, vi in PAIRS:
        ent = None
        for key in (en, en.rstrip("s"), en + "s", en[:-1] if en.endswith("s") else en):
            if key in index:
                ent = index[key]
                break
        if not ent:
            print(f"NOT FOUND: {en}")
            continue
        f, e = ent
        if norm(vi) in {norm(t["term"]) for t in e.get("vi_terms", [])}:
            print(f"already present: {en} -> {vi}")
            continue
        e["vi_terms"].append({"term": vi, "source_id": "", "page": "", "pdf_page": 0,
                              "snippet": "", "verified": False, "recommended": False})
        added += 1
        touched.add(f)
        print(f"added variant: {en} -> {vi}")

    for f in touched:
        json.dump(docs[f], open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n{added} course variants added.")


if __name__ == "__main__":
    main()
