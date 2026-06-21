#!/usr/bin/env python3
"""Find a Vietnamese term in the local source corpus, with page numbers.

Used by the Vietnamese Term Miner agents to produce *verifiable* citations:
each hit reports the source biblio_id, the PDF page, and a text snippet (the
evidence). Corpus files live in workflow/corpus/<biblio_id>.txt (gitignored,
built from text-layer PDFs by the triage step) with "@@PAGE n@@" markers.

Usage:
  find-term.py "sắc số"                 # search all sources
  find-term.py "sắc số" bib-ngodactan-2004
  find-term.py "so mau" --loose         # diacritics-insensitive (extraction-robust)
"""
import glob
import json
import os
import re
import sys
import unicodedata

CORPUS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")
PAGE_RE = re.compile(r"@@PAGE (\d+)@@")


def strip(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def search(term, bid=None, loose=False):
    needle = strip(term) if loose else term.lower()
    files = sorted(glob.glob(os.path.join(CORPUS, (bid or "*") + ".txt")))
    out = []
    for f in files:
        source_id = os.path.basename(f)[:-4]
        page = 0
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                m = PAGE_RE.match(line.strip())
                if m:
                    page = int(m.group(1))
                    continue
                hay = strip(line) if loose else line.lower()
                if needle in hay:
                    out.append({
                        "source_id": source_id,
                        "pdf_page": page,
                        "snippet": " ".join(line.split())[:220],
                    })
    return out


def main():
    args = [a for a in sys.argv[1:] if a != "--loose"]
    loose = "--loose" in sys.argv
    if not args:
        sys.exit("usage: find-term.py <term> [biblio_id] [--loose]")
    term = args[0]
    bid = args[1] if len(args) > 1 else None
    res = search(term, bid, loose)
    print(json.dumps({"term": term, "loose": loose, "hits": len(res),
                      "results": res[:40]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
