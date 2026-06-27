#!/usr/bin/env python3
"""Bilingual consistency cross-tabs over the entry data (read-only report).

Surfaces two defect classes that per-entry validation cannot see because they
are *relations between* entries:

  A. same recommended Vietnamese term -> several distinct English headwords
     (homonym collision: one VI lead term used for two different EN concepts).
     Most are legitimate synonyms (geodesic = shortest path); the report lists
     each group so a human decides. Sorted by group size.

  B. same English headword (normalized) -> several entries with DIVERGENT
     recommended VI terms (homograph entries that disagree, e.g. "root" of a
     tree vs of an equation).

Nothing is changed; this is a review aid. Output: a human summary, plus a JSON
report when --json <path> is given.

Usage:
  consistency-report.py
  consistency-report.py --json workflow/loop/review/consistency-report.json
"""
import glob
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"\s+", " ", s).strip()


def load_entries():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
        import yaml
        for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", []):
            out.append(e)
    return out


def recommended(e):
    return next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), None)


def main():
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]

    entries = [e for e in load_entries() if not e.get("see_ref")]

    # A. recommended VI term (folded) -> distinct EN headwords
    by_vi = defaultdict(list)
    for e in entries:
        rec = recommended(e)
        if rec:
            by_vi[fold(rec)].append({"id": e["id"], "en": e["headword_en"], "vi": rec})
    collisions = []
    for k, members in by_vi.items():
        ens = sorted({m["en"] for m in members})
        if len(ens) > 1:
            collisions.append({"vi_term": members[0]["vi"], "n_headwords": len(ens),
                               "headwords": ens, "entry_ids": sorted(m["id"] for m in members)})
    collisions.sort(key=lambda c: -c["n_headwords"])

    # B. EN headword (folded) -> entries with divergent recommended VI
    by_en = defaultdict(list)
    for e in entries:
        by_en[fold(e["headword_en"])].append({"id": e["id"], "en": e["headword_en"], "vi": recommended(e)})
    homograph_divergence = []
    for k, members in by_en.items():
        recs = sorted({fold(m["vi"]) for m in members})
        if len(members) > 1 and len(recs) > 1:
            homograph_divergence.append({"headword_en": members[0]["en"],
                                         "recommended_terms": sorted({m["vi"] for m in members}),
                                         "entry_ids": sorted(m["id"] for m in members)})

    report = {
        "n_entries_checked": len(entries),
        "A_shared_recommended_term": {
            "count": len(collisions),
            "note": "same recommended VI term for >1 distinct EN headword; many are legit synonyms — review each.",
            "groups": collisions,
        },
        "B_homograph_divergent_recommendation": {
            "count": len(homograph_divergence),
            "note": "same EN headword across entries recommending different VI terms.",
            "groups": homograph_divergence,
        },
    }

    print(f"Consistency report over {len(entries)} non-stub entries\n")
    print(f"A. Recommended VI term shared by >1 English headword: {len(collisions)} group(s)")
    for c in collisions:
        print(f"   '{c['vi_term']}'  ->  {', '.join(c['headwords'])}")
    print(f"\nB. Same English headword, divergent recommended VI: {len(homograph_divergence)} group(s)")
    for h in homograph_divergence:
        print(f"   {h['headword_en']!r}  ->  {h['recommended_terms']}  ({', '.join(h['entry_ids'])})")

    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        json.dump(report, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\nWrote {out_json}")


if __name__ == "__main__":
    main()
