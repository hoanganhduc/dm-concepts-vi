#!/usr/bin/env python3
"""Final consistency pass over the chapter files:

1. see_also cleanup: remap an unresolved id to an existing entry when there is a
   unique obvious match (id is a suffix/variant of exactly one entry id), and
   drop ids that point to no entry (keeps the data consistent; the render was
   already clean since the encoder only links existing targets).
2. course-divergence variants: where the MAT3500 course uses a Vietnamese term
   that is NOT among a matching entry's variants, add it as an uncited variant
   (keep the book's recommended term).
"""
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LECT = os.path.expanduser("~/VNU-HUS-MAT3500/Lectures")
EMPH = re.compile(r"\\(?:EMPH|emph|textbf|textit)\{([^{}]*?)\(([^()]*?)\)[^{}]*?\}")


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "d").lower().strip()


def load():
    files = {f: json.load(open(f, encoding="utf-8"))
             for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json"))}
    return files


def all_entries(files):
    for f, d in files.items():
        for e in d["final_entries"]:
            yield f, e


def fix_see_also(files):
    ids = {e["id"] for _, e in all_entries(files)}
    remapped = dropped = 0
    for _, e in all_entries(files):
        new = []
        for s in e.get("see_also", []):
            if s in ids:
                new.append(s)
                continue
            # unique entry whose id ends with the dropped id (e.g. coloring -> graph-coloring)
            cand = [i for i in ids if i.endswith("-" + s) or i == s.replace("_", "-")]
            if len(cand) == 1:
                new.append(cand[0])
                remapped += 1
            else:
                dropped += 1
        if new != e.get("see_also", []):
            e["see_also"] = sorted(dict.fromkeys(new))
    return remapped, dropped


def course_pairs():
    pairs = {}
    for t in glob.glob(os.path.join(LECT, "**", "*.tex"), recursive=True):
        try:
            s = open(t, encoding="utf-8").read()
        except Exception:
            continue
        for m in EMPH.finditer(s):
            vi, en = m.group(1).strip(" ,."), m.group(2).strip().lower()
            if re.fullmatch(r"[a-z][a-z0-9 \-'/]*", en) and vi:
                pairs.setdefault(en, set()).add(re.sub(r"^(các|những|một)\s+", "", vi, flags=re.I).strip())
    return pairs


def add_variants(files):
    by_hw = {}
    for _, e in all_entries(files):
        by_hw[e["headword_en"].lower()] = e
    added = 0
    for en, vis in course_pairs().items():
        ent = by_hw.get(en) or by_hw.get(en.rstrip("s")) or by_hw.get(en + "s")
        if not ent or ent.get("see_ref"):
            continue
        have = {norm(t["term"]) for t in ent.get("vi_terms", [])}
        for vi in vis:
            if vi and norm(vi) not in have:
                ent["vi_terms"].append({"term": vi, "source_id": "", "page": "", "pdf_page": 0,
                                        "snippet": "", "verified": False, "recommended": False})
                have.add(norm(vi))
                added += 1
    return added


def main():
    files = load()
    rem, drop = fix_see_also(files)
    added = add_variants(files)
    for f, d in files.items():
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"see_also: remapped {rem}, dropped {drop}; course variants added {added}")


if __name__ == "__main__":
    main()
