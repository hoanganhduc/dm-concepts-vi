#!/usr/bin/env python3
"""Merge staged new entries (data/<staging-dir>/*.json) into the chapter files.

Dedups by id and by singular/plural headword against the existing book and within
the batch, validates each staged entry (one recommended; verified terms carry a
registry source + page; headword matches its letter), and appends the survivors
to workflow/panels/chapter-<l>-final.json. Rejects are reported, not added.

Usage: merge-staging.py <staging-subdir>   (e.g. mat3500-staging, rosen-staging)
"""
import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def reg_ids():
    r = yaml.safe_load(open(os.path.join(ROOT, "data", "sources", "registry.yaml"))) or {}
    return {s["biblio_id"] for s in r.get("sources", []) if s.get("biblio_id")}


def vary(t):
    t = (t or "").lower().strip()
    return {t, t.rstrip("s"), t + "s", (t[:-1] if t.endswith("s") else t)}


def validate(e, src_ids, all_ids):
    errs = []
    hw, L = e.get("headword_en", ""), str(e.get("letter", "")).upper()
    if not KEBAB.match(e.get("id", "") or ""):
        errs.append("bad id")
    if not hw:
        errs.append("no headword")
    if hw and L and hw[:1].upper() != L:
        errs.append("letter-mismatch")
    if e.get("see_ref"):  # cross-reference stub: skip definition/vi_terms checks
        if e["see_ref"] not in all_ids:
            errs.append(f"see_ref-missing:{e['see_ref']}")
        return errs
    if not e.get("definition_vi"):
        errs.append("no def")
    vts = e.get("vi_terms") or []
    if not vts:
        errs.append("no vi_terms")
    if sum(1 for t in vts if t.get("recommended")) != 1:
        errs.append("recommended!=1")
    for t in vts:
        if t.get("verified"):
            if t.get("source_id") not in src_ids:
                errs.append(f"src:{t.get('source_id')}")
            if not str(t.get("page", "")).strip():
                errs.append("verified-no-page")
    return errs


def main():
    sub = sys.argv[1] if len(sys.argv) > 1 else "mat3500-staging"
    src_ids = reg_ids()
    chapters, eids, ehw = {}, set(), set()
    for f in glob.glob(os.path.join(ROOT, "workflow", "panels", "chapter-*-final.json")):
        L = os.path.basename(f).split("-")[1].upper()
        d = json.load(open(f, encoding="utf-8"))
        chapters[L] = [f, d]
        for e in d["final_entries"]:
            eids.add(e["id"])
            ehw |= vary(e["headword_en"])

    added = dup = bad = 0
    reasons = {}
    batch_hw = set()
    for sf in sorted(glob.glob(os.path.join(ROOT, "data", sub, "*.json"))):
        try:
            e = json.load(open(sf, encoding="utf-8"))
        except Exception:
            bad += 1
            continue
        hw = e.get("headword_en", "").lower().strip()
        L = str(e.get("letter", "")).upper() or hw[:1].upper()
        e["letter"] = L
        if e.get("id") in eids or (vary(hw) & ehw) or (vary(hw) & batch_hw):
            dup += 1
            continue
        errs = validate(e, src_ids, eids)
        if errs or L not in chapters:
            bad += 1
            reasons[e.get("id", os.path.basename(sf))] = errs or ["no-chapter"]
            continue
        e.setdefault("status", "draft")
        chapters[L][1]["final_entries"].append(e)
        eids.add(e["id"])
        batch_hw |= vary(hw)
        added += 1

    for L, (f, d) in chapters.items():
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"added {added}, dup-skipped {dup}, invalid {bad}")
    for k, v in list(reasons.items())[:40]:
        print(f"  REJECT {k}: {v}")


if __name__ == "__main__":
    main()
