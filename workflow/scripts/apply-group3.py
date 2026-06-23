#!/usr/bin/env python3
"""Apply Nhóm-3 'change' decisions (workflow/loop/review/group3-decisions.json)
to the panel final.json source of truth. 'keep'/'applied' are no-ops.

For a change to {to, src}:
  - src non-empty: move the recommended flag onto the verified vi_term cited
    from that source whose term matches `to` (the term already exists).
  - src empty: make `to` the recommended uncited canonical term — rename an
    existing diacritic-insensitive match in place (handles casing), else insert.
"""
import json, glob, unicodedata, re

def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower(); s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

dec = json.load(open('workflow/loop/review/group3-decisions.json'))['decisions']
loc, data = {}, {}
for f in sorted(glob.glob('workflow/panels/chapter-*-final.json')):
    d = json.load(open(f)); data[f] = d
    for e in d.get('final_entries', []):
        loc[e['id']] = (f, e)

changed, log = set(), []
for item in dec:
    if item['action'] != 'change':
        continue
    eid, to, src = item['id'], item['to'], item.get('src', '')
    if eid not in loc:
        log.append(f"  ! {eid}: NOT FOUND"); continue
    f, e = loc[eid]; vts = e.get('vi_terms', [])
    cur = next((t for t in vts if t.get('recommended')), None)
    if src:
        tgt = next((t for t in vts if t.get('verified') and t.get('source_id') == src
                    and norm(t['term']) == norm(to)), None)
        if not tgt:
            log.append(f"  ! {eid}: cited '{to}' [{src}] not found — fallback to uncited"); src = ''
    if not src:
        tgt = next((t for t in vts if norm(t['term']) == norm(to)), None)
        if tgt is None:
            tgt = {'term': to, 'source_id': '', 'page': '', 'pdf_page': 0, 'snippet': '', 'verified': False}
            vts.insert(0, tgt)
        else:
            tgt['term'] = to  # apply exact casing/spelling
        tgt['verified'] = False; tgt['source_id'] = ''; tgt['page'] = ''; tgt['pdf_page'] = 0
    for t in vts:
        t['recommended'] = False
    tgt['recommended'] = True
    changed.add(f)
    log.append(f"  ✓ {eid}: '{cur['term'] if cur else '—'}' → '{to}'{' ['+src+']' if src else ' (uncited)'}")

for f in changed:
    json.dump(data[f], open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

n_change = sum(1 for i in dec if i['action'] == 'change')
n_keep = sum(1 for i in dec if i['action'] == 'keep')
n_applied = sum(1 for i in dec if i['action'] == 'applied')
print('\n'.join(log))
print(f"\nNhóm-3: {len(dec)} mục | change={n_change} keep={n_keep} applied-directly={n_applied} | files touched={len(changed)}")
