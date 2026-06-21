#!/usr/bin/env python3
"""Print one panel-approved entry as JSON. Used by enrichment miner agents.

Usage: get-entry.py <entry-id> [letter]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    eid = sys.argv[1]
    letter = (sys.argv[2] if len(sys.argv) > 2 else "c").lower()
    path = os.path.join(ROOT, "workflow", "panels", f"chapter-{letter}-final.json")
    d = json.load(open(path, encoding="utf-8"))
    e = [x for x in d["final_entries"] if x["id"] == eid]
    print(json.dumps(e[0] if e else {}, ensure_ascii=False))


if __name__ == "__main__":
    main()
