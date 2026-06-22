#!/usr/bin/env python3
"""Add the Rosen Vietnamese translation as a REFERENCE citation across all
chapters.

For every already-verified vi_term in every entry, look for that exact term
(word-boundary, case-insensitive) in the Rosen corpus. If found, append a
reference citation (source_id=bib-rosen-2003-vi, verified=true,
recommended=false) — Rosen is a comparison source only and is never promoted to
the lead/recommended term. Idempotent: skips terms that already carry a Rosen
row. Edits workflow/panels/chapter-*-final.json in place.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROSEN_FILE = os.path.join(ROOT, "workflow", "corpus", "bib-rosen-2003-vi.txt")
ROSEN_ID = "bib-rosen-2003-vi"

# Pre-index Rosen as (page, raw_line) pairs.
PAGE_RE = re.compile(r"@@PAGE (\d+)@@")
LINES = []
_page = 0
for _ln in open(ROSEN_FILE, encoding="utf-8"):
    m = PAGE_RE.match(_ln.strip())
    if m:
        _page = int(m.group(1))
        continue
    LINES.append((_page, _ln))


def find_rosen(term):
    """First word-boundary occurrence of `term` in Rosen; returns (page, snippet)."""
    if len(term.strip()) < 3:
        return None
    pat = re.compile(r"\b" + re.escape(term.strip()) + r"\b", re.IGNORECASE)
    for page, raw in LINES:
        if pat.search(raw):
            return page, " ".join(raw.split())[:200]
    return None


def main():
    added = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json"))):
        doc = json.load(open(f, encoding="utf-8"))
        changed = False
        for e in doc.get("final_entries", []):
            have_rosen = {t["term"] for t in e.get("vi_terms", []) if t.get("source_id") == ROSEN_ID}
            distinct = []
            for t in e.get("vi_terms", []):
                if t.get("verified") and t.get("term") not in have_rosen and t["term"] not in distinct:
                    distinct.append(t["term"])
            for term in distinct:
                hit = find_rosen(term)
                if not hit:
                    continue
                page, snippet = hit
                e["vi_terms"].append({
                    "term": term, "source_id": ROSEN_ID, "pdf_page": page,
                    "page": f"tr. {page} (PDF, bản dịch Rosen)", "snippet": snippet,
                    "verified": True, "recommended": False,
                })
                have_rosen.add(term)
                added += 1
                changed = True
        if changed:
            json.dump(doc, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Added {added} Rosen reference citations across chapters.")


if __name__ == "__main__":
    main()
