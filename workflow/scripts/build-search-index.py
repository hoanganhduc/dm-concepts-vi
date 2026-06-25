#!/usr/bin/env python3
"""Generate assets/search/entries.json from data/terms/*.yaml.

The JSON feeds the client-side quick-lookup page (assets/search/tra-cuu.html),
which does diacritics-insensitive, bilingual instant filtering. data/terms/*.yaml
is the single source of truth (it also drives the PreTeXt source).
"""
import glob
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")


def to_mathjax(text):
    """Convert the book's $$...$$ math delimiters to \\(...\\) for MathJax."""
    text = " ".join((text or "").split())
    return re.sub(r"\$\$(.+?)\$\$", r"\\(\1\\)", text)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TERM_FILES = glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))


def main() -> int:
    out = []
    for path in sorted(TERM_FILES):
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        for e in doc.get("entries", []):
            letter = (e.get("letter") or (e.get("headword_en", "?")[:1])).upper()
            out.append({
                "id": e["id"],
                "letter": letter,
                "headword_en": e.get("headword_en", ""),
                "notation": e.get("notation", ""),
                "vi_terms": sorted({t.get("term", "") for t in e.get("vi_terms", [])}),
                "definition_vi": to_mathjax(e.get("definition_vi")),
                # PreTeXt renders a <definition xml:id="def-<id>"> on ch-<letter>.html.
                "url": "ch-{0}.html#def-{1}".format(letter.lower(), e["id"]),
            })

    # Unsettled-terms appendix: entries carry candidate translations (no single
    # recommended term) and live on appendix-unsettled.html#apx-<id>.
    apx_path = os.path.join(ROOT, "data", "terms", "appendix-unsettled.yaml")
    if os.path.exists(apx_path):
        with open(apx_path, encoding="utf-8") as fh:
            apx = yaml.safe_load(fh) or {}
        for e in apx.get("entries", []):
            out.append({
                "id": e["id"],
                "letter": e.get("headword_en", "?")[:1].upper(),
                "headword_en": e.get("headword_en", ""),
                "notation": e.get("notation", ""),
                "vi_terms": sorted({c.get("term", "") for c in e.get("candidates", [])}),
                "definition_vi": to_mathjax(e.get("definition_vi")),
                "url": "appendix-unsettled.html#apx-{0}".format(e["id"]),
            })

    out.sort(key=lambda x: (x["letter"], x["headword_en"].lower()))
    dest = os.path.join(ROOT, "assets", "search", "entries.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("Wrote {0} entries -> {1}".format(len(out), os.path.relpath(dest, ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
