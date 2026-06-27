#!/usr/bin/env python3
"""Headword coverage / recall of the book against the Rosen term list (read-only).

The book claims to cover the discrete-math & CS vocabulary; this quantifies it.
It compares the book's English headwords against the extracted Rosen master term
list (data/rosen-master.json, the gold list) and reports recall plus the Rosen
terms that have no matching book headword. Nothing is changed.

Matching (English): lowercased, bracketed/parenthetical content removed,
punctuation stripped, leading article dropped, trailing plural "s" tolerated.
A Rosen term counts as covered if its normalized form equals a book headword, or
is a whole-word substring of one (or vice versa). Exact vs fuzzy matches are
reported separately so recall is not over-credited.

Usage:
  rosen-coverage.py
  rosen-coverage.py --gold data/rosen-key-terms.json   # use the key-terms list
  rosen-coverage.py --json workflow/loop/review/rosen-coverage.json
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ARTICLES = ("the ", "a ", "an ")


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", s)      # drop (…) and […]
    s = re.sub(r"[^a-z0-9 ]", " ", s)                 # punctuation -> space
    s = re.sub(r"\s+", " ", s).strip()
    for a in ARTICLES:
        if s.startswith(a):
            s = s[len(a):]
    return s


def singularize(s):
    # tolerate a trailing plural on the last word only
    return re.sub(r"s\b", "", s) if s.endswith("s") else s


def whole_word_in(needle, hay):
    return re.search(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])", hay) is not None


def load_book_headwords():
    import yaml
    hs = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
        for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", []):
            hs.append(e["headword_en"])
    return hs


def load_gold(path):
    data = json.load(open(path, encoding="utf-8"))
    out = []
    for d in data:
        en = d.get("en") or d.get("term") or d.get("headword_en")
        if en:
            out.append(en)
    return out


def main():
    gold_path = os.path.join(ROOT, "data", "rosen-master.json")
    if "--gold" in sys.argv:
        gold_path = os.path.join(ROOT, sys.argv[sys.argv.index("--gold") + 1]) \
            if not os.path.isabs(sys.argv[sys.argv.index("--gold") + 1]) else sys.argv[sys.argv.index("--gold") + 1]
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None

    book = load_book_headwords()
    book_norm = {norm(h) for h in book}
    book_sing = {singularize(n) for n in book_norm}

    gold = load_gold(gold_path)
    exact, fuzzy, missing = [], [], []
    for g in gold:
        gn = norm(g)
        gs = singularize(gn)
        if gn in book_norm or gs in book_sing:
            exact.append(g)
            continue
        # fuzzy: gold term is a whole-word part of some book headword or vice versa
        hit = next((h for h in book_norm
                    if whole_word_in(gn, h) or whole_word_in(gs, singularize(h))
                    or whole_word_in(h, gn)), None)
        if hit:
            fuzzy.append({"rosen": g, "book_headword_norm": hit})
        else:
            missing.append(g)

    total = len(gold)
    covered = len(exact) + len(fuzzy)
    report = {
        "gold_list": os.path.relpath(gold_path, ROOT),
        "n_gold_terms": total,
        "n_book_headwords": len(book),
        "exact_matches": len(exact),
        "fuzzy_matches": len(fuzzy),
        "recall_exact": round(len(exact) / total, 3) if total else None,
        "recall_with_fuzzy": round(covered / total, 3) if total else None,
        "missing_terms": sorted(missing, key=str.lower),
        "fuzzy_pairs": fuzzy,
    }

    print(f"Rosen coverage — gold list {report['gold_list']} ({total} terms) "
          f"vs {len(book)} book headwords\n")
    print(f"  exact matches : {len(exact)}  ({report['recall_exact']:.1%})")
    print(f"  +fuzzy matches: {covered}  ({report['recall_with_fuzzy']:.1%})")
    print(f"  MISSING (no book headword): {len(missing)}\n")
    for m in report["missing_terms"]:
        print(f"    - {m}")

    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        json.dump(report, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\nWrote {out_json}")


if __name__ == "__main__":
    main()
