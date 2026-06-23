#!/usr/bin/env python3
"""Prepare the 10-loop Codex review: split all entries into 10 ordered batches,
write each to workflow/loop/review/batch-<i>.json, and initialise the loop ledger.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REVIEW = os.path.join(ROOT, "workflow", "loop", "review")
BATCH = 40  # entries per Codex call (77 overflowed Codex's context window)
CORPUS = {"bib-leanhvinh-2020", "bib-nguyenhoangthach-2020", "bib-nguyenhuudien-2019",
          "bib-hoangchithanh-2007", "bib-nguyenducnghia-2006", "bib-ngodactan-2004",
          "bib-rosen-2003-vi"}


def main():
    os.makedirs(REVIEW, exist_ok=True)
    entries = []
    for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")):
        for e in json.load(open(f, encoding="utf-8"))["final_entries"]:
            entries.append(e)
    entries.sort(key=lambda e: (e.get("letter", ""), e["headword_en"].lower()))

    n = len(entries)
    size = BATCH
    NLOOPS = -(-n // BATCH)  # ceil
    for i in range(NLOOPS):
        chunk = entries[i * size:(i + 1) * size]
        slim = [{
            "id": e["id"], "letter": e.get("letter", ""), "headword_en": e["headword_en"],
            "rosen_ref": e.get("rosen_ref", ""), "definition_vi": e.get("definition_vi", ""),
            "see_ref": e.get("see_ref", ""),
            "vi_terms": [{"term": t.get("term"), "source_id": t.get("source_id", ""),
                          "page": t.get("page", ""), "pdf_page": t.get("pdf_page"),
                          "verified": bool(t.get("verified")), "recommended": bool(t.get("recommended"))}
                         for t in e.get("vi_terms", [])],
        } for e in chunk]
        json.dump(slim, open(os.path.join(REVIEW, f"batch-{i+1}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    state = {
        "goal": "Codex line-by-line review of all entries over 10 sequential loops: "
                "(1) citation accuracy vs corpus, (2) term commonality vs authoritative sources, "
                "(3) missing alternative Vietnamese translations.",
        "reviewer": "codex (gpt-5.5, xhigh) via codex exec; Claude orchestrates + validates + fixes",
        "n_loops": NLOOPS, "n_entries": n, "batch_size": size,
        "corpus_sources": sorted(CORPUS),
        "done_loops": [], "current": 1, "status": "running",
        "stop_conditions": ["all 10 loops processed", "user stop"],
    }
    json.dump(state, open(os.path.join(REVIEW, "loop_state.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(os.path.join(REVIEW, "iterations.jsonl"), "a").close()
    print(f"{n} entries -> {NLOOPS} batches of <= {size}. Ledger at workflow/loop/review/")


if __name__ == "__main__":
    main()
