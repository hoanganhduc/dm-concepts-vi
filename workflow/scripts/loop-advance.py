#!/usr/bin/env python3
"""Advance the autonomous chapter loop after a letter is finished or skipped.

Updates workflow/loop/loop_state.json (move letter done/skipped, pick next),
appends iterations.jsonl, updates recovery.md, and prints the NEXT pending
letter (or DONE).

Usage: loop-advance.py <LETTER> [--skip]
"""
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOOP = os.path.join(ROOT, "workflow", "loop")


def main():
    L = sys.argv[1].upper()
    skip = "--skip" in sys.argv
    sp = os.path.join(LOOP, "loop_state.json")
    st = json.load(open(sp, encoding="utf-8"))
    for k in ("in_progress", "pending"):
        st[k] = [x for x in st.get(k, []) if x != L]
    bucket = "skipped" if skip else "done"
    st.setdefault(bucket, [])
    if L not in st[bucket]:
        st[bucket].append(L)
    nxt = st["pending"][0] if st.get("pending") else None
    st["in_progress"] = [nxt] if nxt else []
    st["current"] = nxt
    st["status"] = "running" if nxt else "completed"
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    rec = {"ts": ts, "letter": L, "decision": ("skip" if skip else "done"), "next": nxt}
    open(os.path.join(LOOP, "iterations.jsonl"), "a", encoding="utf-8").write(
        json.dumps(rec, ensure_ascii=False) + "\n")
    open(os.path.join(LOOP, "recovery.md"), "a", encoding="utf-8").write(
        f"\n- {ts} {bucket} {L}; next={nxt or 'DONE'}; "
        f"done={len(st['done'])} skipped={len(st.get('skipped', []))} pending={len(st.get('pending', []))}")
    print(nxt or "DONE")


if __name__ == "__main__":
    main()
