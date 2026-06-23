#!/usr/bin/env python3
"""Deterministic citation audit (review dimension 1): for every verified vi_term
whose source has local corpus text, confirm the term actually appears at/near the
cited PDF page. Flags terms not found, or found only far from the cited page.
Writes workflow/loop/review/citation-issues.json.
"""
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "workflow", "corpus")
PAGE_RE = re.compile(r"@@PAGE (\d+)@@")
NEAR = 3


def strip(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "d").lower()


def load_corpus():
    corp = {}
    for f in glob.glob(os.path.join(CORPUS, "*.txt")):
        sid = os.path.basename(f)[:-4]
        pages, page = [], 0
        for ln in open(f, encoding="utf-8"):
            m = PAGE_RE.match(ln.strip())
            if m:
                page = int(m.group(1))
                continue
            pages.append((page, strip(ln)))
        corp[sid] = pages
    return corp


def main():
    corp = load_corpus()
    issues, n_cites = [], 0
    for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")):
        for e in json.load(open(f, encoding="utf-8"))["final_entries"]:
            if e.get("see_ref"):
                continue
            for t in e.get("vi_terms", []):
                sid = t.get("source_id")
                if not (t.get("verified") and sid in corp and t.get("term")):
                    continue
                n_cites += 1
                needle = strip(t["term"])
                pages = sorted({p for p, ln in corp[sid] if needle in ln})
                cited = t.get("pdf_page")
                if not pages:
                    issues.append({"id": e["id"], "term": t["term"], "source": sid,
                                   "cited_page": cited, "problem": "term-not-found"})
                elif cited and not any(abs(p - cited) <= NEAR for p in pages):
                    issues.append({"id": e["id"], "term": t["term"], "source": sid,
                                   "cited_page": cited, "found_pages": pages[:8],
                                   "problem": "page-mismatch"})
    os.makedirs(os.path.join(ROOT, "workflow", "loop", "review"), exist_ok=True)
    json.dump(issues, open(os.path.join(ROOT, "workflow", "loop", "review", "citation-issues.json"),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nf = sum(1 for i in issues if i["problem"] == "term-not-found")
    pm = sum(1 for i in issues if i["problem"] == "page-mismatch")
    print(f"checked {n_cites} corpus-cited terms | issues: {len(issues)} "
          f"(term-not-found: {nf}, page-mismatch: {pm})")


if __name__ == "__main__":
    main()
