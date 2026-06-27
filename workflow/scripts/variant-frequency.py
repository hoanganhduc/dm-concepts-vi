#!/usr/bin/env python3
"""Corpus frequency dominance of competing Vietnamese variants (read-only).

Existing mining (find-term.py / remine-corpus.py) confirms a variant is
*attested somewhere*. This goes one step further: it counts how often each
variant of an entry occurs across the whole Vietnamese corpus and flags entries
where the *recommended* term is NOT the most frequent — i.e. it may not be the
dominant usage. A heuristic review aid; nothing is changed.

Matching: diacritics/case-folded, whole-token (Vietnamese is space-separated),
counted over all corpus files (workflow/corpus/<id>.txt, "@@PAGE n@@" markers
stripped). bib-rosen-2003-vi is excluded by default (reference-only translation,
never the lead source) — pass --include-rosen to count it too.

A variant is flagged as a stronger competitor when its count >= max(FLOOR,
RATIO * recommended_count). Entries whose recommended term has zero corpus hits
while some variant has hits are also listed.

Usage:
  variant-frequency.py
  variant-frequency.py --json workflow/loop/review/variant-frequency.json
  variant-frequency.py --floor 3 --ratio 2.0
"""
import glob
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "workflow", "corpus")
PAGE_RE = re.compile(r"@@PAGE \d+@@")
EXCLUDE_DEFAULT = {"bib-rosen-2003-vi"}


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


TOKEN_RE = re.compile(r"[0-9a-z]+")


def term_tuple(term):
    return tuple(TOKEN_RE.findall(fold(term)))


def count_terms(needed, include_rosen):
    """Count corpus occurrences of exactly the `needed` whole-token terms.

    Scanning a 16 MB blob with a regex per term (thousands of terms) is far too
    slow. Instead tokenize the corpus once and, at each position, test only the
    n-gram lengths that some query term actually has against a set membership —
    O(corpus x #distinct-lengths), memory bounded to the query terms.
    """
    needed = {t for t in needed if t}
    lengths = sorted({len(t) for t in needed})
    counts = {t: 0 for t in needed}
    for f in sorted(glob.glob(os.path.join(CORPUS, "*.txt"))):
        sid = os.path.basename(f)[:-4]
        if not include_rosen and sid in EXCLUDE_DEFAULT:
            continue
        toks = TOKEN_RE.findall(fold(PAGE_RE.sub(" ", open(f, encoding="utf-8").read())))
        n = len(toks)
        for k in lengths:
            for i in range(n - k + 1):
                g = tuple(toks[i:i + k])
                if g in needed:
                    counts[g] += 1
    return counts


def main():
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]
    floor = int(sys.argv[sys.argv.index("--floor") + 1]) if "--floor" in sys.argv else 3
    ratio = float(sys.argv[sys.argv.index("--ratio") + 1]) if "--ratio" in sys.argv else 2.0
    include_rosen = "--include-rosen" in sys.argv

    import yaml
    entries = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
        entries += [e for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", [])
                    if not e.get("see_ref")]

    # gather every distinct variant term, count all in one corpus pass
    all_terms = {t["term"] for e in entries for t in e.get("vi_terms", [])}
    tup = {t: term_tuple(t) for t in all_terms}
    tuple_counts = count_terms(set(tup.values()), include_rosen)

    def c(term):
        return tuple_counts.get(tup.get(term, ()), 0)

    def is_sub(a, b):
        return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1)) if a and len(a) <= len(b) else False

    def comparable(rec, v):
        # only a genuine competing translation: similar length and not a
        # fragment/extension of the recommended term (avoids "tập" beating
        # "tập hợp" or a lone generic word beating a precise multi-word term).
        a, b = tup.get(rec, ()), tup.get(v, ())
        if not a or not b or abs(len(a) - len(b)) > 1:
            return False
        return not (is_sub(a, b) or is_sub(b, a))

    flagged, zero_rec = [], []
    for e in entries:
        terms = [t["term"] for t in e.get("vi_terms", [])]
        rec = next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), None)
        if not rec:
            continue
        counts = {t: c(t) for t in dict.fromkeys(terms)}  # dedupe, keep order
        rec_n = counts.get(rec, 0)
        # stronger competitor among comparable (similar-length, non-fragment) variants
        comps = sorted(((t, n) for t, n in counts.items() if t != rec and comparable(rec, t)),
                       key=lambda x: -x[1])
        top = comps[0] if comps else None
        best_any = max(((t, n) for t, n in counts.items() if t != rec),
                       key=lambda x: x[1], default=None)
        if top and top[1] >= max(floor, ratio * max(rec_n, 1)) and top[1] > rec_n:
            flagged.append({"id": e["id"], "en": e["headword_en"],
                            "recommended": rec, "rec_count": rec_n,
                            "stronger_variant": top[0], "variant_count": top[1],
                            "all_counts": counts})
        elif rec_n == 0 and best_any and best_any[1] > 0:
            zero_rec.append({"id": e["id"], "en": e["headword_en"],
                             "recommended": rec, "best_variant": best_any[0],
                             "variant_count": best_any[1]})

    flagged.sort(key=lambda x: -(x["variant_count"] - x["rec_count"]))
    report = {
        "n_entries_checked": len(entries),
        "params": {"floor": floor, "ratio": ratio, "include_rosen": include_rosen},
        "stronger_competitor": {"count": len(flagged),
                                "note": "a non-recommended variant is substantially more frequent in the corpus.",
                                "entries": flagged},
        "recommended_zero_hits": {"count": len(zero_rec),
                                  "note": "recommended term has 0 corpus hits while a variant has some.",
                                  "entries": zero_rec},
    }

    print(f"Variant-frequency report over {len(entries)} non-stub entries "
          f"(floor={floor}, ratio={ratio})\n")
    print(f"Recommended term out-frequented by a variant: {len(flagged)}")
    for x in flagged[:40]:
        print(f"   {x['en']:<28} rec '{x['recommended']}'({x['rec_count']}) "
              f"<  '{x['stronger_variant']}'({x['variant_count']})")
    print(f"\nRecommended term with 0 corpus hits (variant has some): {len(zero_rec)}")
    for x in zero_rec[:25]:
        print(f"   {x['en']:<28} rec '{x['recommended']}'(0)  vs '{x['best_variant']}'({x['variant_count']})")

    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        json.dump(report, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\nWrote {out_json}")


if __name__ == "__main__":
    main()
