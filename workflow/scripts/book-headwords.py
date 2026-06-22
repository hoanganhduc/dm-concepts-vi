#!/usr/bin/env python3
"""Print all current book entries as JSON [{id, en, vi}] so an agent can detect
whether a concept already exists (by English headword or shared Vietnamese term)
before creating a duplicate."""
import glob
import json
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = []
for f in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
    for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", []):
        rec = next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), "")
        out.append({"id": e["id"], "en": e["headword_en"], "vi": rec})
print(json.dumps(out, ensure_ascii=False))
