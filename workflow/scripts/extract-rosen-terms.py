#!/usr/bin/env python3
"""Extract Rosen's authoritative glossary from the 'Key Terms and Results'
sections of the 8th edition, as the master term list for coverage checking.

Each chapter ends with a two-column 'Key Terms and Results / TERMS' list of
`term: definition` entries. We split the layout columns and capture each term
plus its same-line definition snippet.

Output: data/rosen-key-terms.json = [{term, definition, chapter}].
Requires a pdftotext dump of the textbook at /tmp/rosen2018.txt.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TXT = "/tmp/rosen2018.txt"
END_RE = re.compile(r"\n\s*(Review Questions|Supplementary Exercises|Computer Projects|Writing Projects)\b")
# A glossary entry inside a column cell: "term: definition..."
ENTRY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 \-'/(),.&]{1,55}?):\s+(\S.*)$")


def main():
    txt = open(TXT, encoding="utf-8").read()
    parts = txt.split("Key Terms and Results")
    terms = {}
    for ci, p in enumerate(parts[1:], 1):
        end = END_RE.search(p)
        sec = p[:end.start()] if end else p[:9000]
        for line in sec.splitlines():
            for cell in re.split(r"\s{3,}", line.strip()):
                m = ENTRY_RE.match(cell.strip())
                if not m:
                    continue
                term = re.sub(r"\s+", " ", m.group(1)).strip().lower()
                # keep glossary-like terms; drop sentence fragments / notation noise
                if not (2 <= len(term) <= 50):
                    continue
                if term.split()[0] in ("the", "a", "an", "if", "for", "and", "or", "to", "this", "these"):
                    continue
                if term not in terms:
                    terms[term] = {"term": term, "definition": m.group(2).strip()[:160], "chapter": ci}
    out = sorted(terms.values(), key=lambda x: x["term"])
    json.dump(out, open(os.path.join(ROOT, "data", "rosen-key-terms.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"Rosen master terms: {len(out)}")
    for d in out[:25]:
        print(f"  {d['term']:34} | {d['definition'][:50]}")


if __name__ == "__main__":
    main()
