#!/usr/bin/env python3
"""Definition-adequacy / non-circularity checks (read-only report).

Lexicographic hygiene on `definition_vi`, following the ISO 704 / Suonuuti
genus-differentia rules: a good definition names the term, then "là" (is a),
then a more-general genus and the distinguishing characteristics — and must NOT
define the term with itself (circularity) nor be too terse / too dense.

Checks per non-stub entry:
  - CIRCULAR: the recommended term is its OWN genus — the definition reads
    "<term> là [một] <term> …", defining the term with itself. (Merely
    mentioning the term again later is legitimate elaboration and is NOT flagged.)
  - NO-COPULA: the definition does not contain a defining copula ("là"/"được
    gọi là"/"là một") — it may not be a proper genus-differentia definition.
  - TOO-SHORT: definition under MIN chars (likely under-specified).
  - TOO-LONG: definition over MAX chars (comprehension cost; consider splitting).

Heuristic — a review aid; nothing is changed. Writes JSON when --json is given.

Usage:
  definition-adequacy.py
  definition-adequacy.py --json workflow/loop/review/definition-adequacy.json
  definition-adequacy.py --min 90 --max 600
"""
import glob
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COPULA = ("được gọi là", "là một", "là tập", "là phép", "là quá trình", "là việc", "là ", "là,")


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.replace("đ", "d").replace("Đ", "D").lower()).strip()


def strip_math(s):
    # drop $$...$$ and \emph{...} wrappers so length/word checks see prose only
    s = re.sub(r"\$\$.*?\$\$", " ", s or "")
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    MIN = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 90
    MAX = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 600

    import yaml
    entries = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
        entries += [e for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", [])
                    if not e.get("see_ref")]

    circular, no_copula, too_short, too_long = [], [], [], []
    for e in entries:
        defn = e.get("definition_vi") or ""
        prose = strip_math(defn)
        rec = next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), None)
        fdef = fold(prose)

        if not any(c in fdef for c in (fold(x) for x in COPULA)):
            no_copula.append({"id": e["id"], "en": e["headword_en"], "definition_vi": prose[:120]})
        if len(prose) < MIN:
            too_short.append({"id": e["id"], "en": e["headword_en"], "len": len(prose), "definition_vi": prose})
        if len(prose) > MAX:
            too_long.append({"id": e["id"], "en": e["headword_en"], "len": len(prose)})

        if rec:
            ft = fold(rec)
            # genus tautology: the term is its own genus — "<term> là [một/một
            # loại/một dạng] <term>". Precise, low-recall; the LLM monolingual
            # review covers subtler conditional circularity ("... nếu nó ...").
            # only the DECLARATIVE "<term> là [một] <term>" form is genus
            # tautology; the "(được) gọi là <term> nếu/khi …" form is conditional
            # naming (definiendum), not circular, so it is excluded.
            m = re.search(r"(?<!goi )\bla\s+(?:mot\s+)?(?:loai\s+|dang\s+|kieu\s+)?"
                          + re.escape(ft) + r"\b", fdef)
            if m and not re.search(r"\bneu\b|\bkhi\b|goi la", fdef[:m.start() + 3]):
                circular.append({"id": e["id"], "en": e["headword_en"], "term": rec,
                                 "definition_vi": prose[:160]})

    report = {
        "n_entries_checked": len(entries),
        "params": {"min": MIN, "max": MAX},
        "circular_smell": {"count": len(circular), "note": "recommended term recurs in its own differentia — review for circularity.", "entries": circular},
        "no_copula": {"count": len(no_copula), "note": "no defining 'là' copula found.", "entries": no_copula},
        "too_short": {"count": len(too_short), "note": f"definition under {MIN} chars.", "entries": too_short},
        "too_long": {"count": len(too_long), "note": f"definition over {MAX} chars.", "entries": too_long},
    }

    print(f"Definition-adequacy report over {len(entries)} non-stub entries (min={MIN}, max={MAX})\n")
    for key, label in [("circular_smell", "Circularity smell (term recurs in its own definition)"),
                       ("no_copula", "No defining copula"),
                       ("too_short", "Too short"), ("too_long", "Too long")]:
        sec = report[key]
        print(f"{label}: {sec['count']}")
        for x in sec["entries"][:15]:
            extra = f" (×{x['occurrences']})" if "occurrences" in x else (f" ({x['len']} ch)" if "len" in x else "")
            print(f"   {x['en']:<30}{extra}  {x.get('term','')}")
        print()

    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        json.dump(report, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
