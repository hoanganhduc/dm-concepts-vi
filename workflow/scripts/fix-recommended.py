#!/usr/bin/env python3
"""Apply the safe review fixes (RE-POINT + verified SEMANTIC) to the panel
final.json source of truth. Re-points the `recommended` flag onto a properly
cited (non-reference) variant; for re-points the demoted uncited duplicate is
dropped. Reads workflow/loop/review/fix-plan.json."""
import json, glob, unicodedata, re

def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower(); s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

plan = json.load(open('workflow/loop/review/fix-plan.json'))

# id -> (filepath, file-data, entry)
loc = {}
data = {}
for f in sorted(glob.glob('workflow/panels/chapter-*-final.json')):
    d = json.load(open(f)); data[f] = d
    for e in d.get('final_entries', []):
        loc[e['id']] = (f, e)

changed = set()
log = []

def switch(eid, target_term, target_src, kind):
    if eid not in loc:
        log.append(f"  ! {eid}: NOT FOUND"); return
    f, e = loc[eid]
    vts = e.get('vi_terms', [])
    cur = next((t for t in vts if t.get('recommended')), None)
    tgt = next((t for t in vts if t.get('verified') and t.get('source_id') == target_src
                and norm(t['term']) == norm(target_term)), None)
    if not tgt:
        log.append(f"  ! {eid}: target '{target_term}' [{target_src}] not found — skip"); return
    for t in vts:
        t['recommended'] = False
    tgt['recommended'] = True
    # drop a demoted, uncited duplicate (machine-translation artifact)
    if cur is not None and cur is not tgt and not cur.get('source_id'):
        vts.remove(cur)
    changed.add(f)
    log.append(f"  ✓ {eid}: '{cur['term'] if cur else '—'}' → '{tgt['term']}' ({target_src}) [{kind}]")

for x in plan.get('repoint', []):
    switch(x['id'], x['term'], x['source_id'], 'repoint')
for x in plan.get('semantic', []):
    switch(x['id'], x['to'], x['source_id'], 'semantic')

# write back only modified files
for f in changed:
    json.dump(data[f], open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# integrity: exactly one recommended per non-stub entry touched
bad = 0
for x in plan.get('repoint', []) + [{'id': s['id']} for s in plan.get('semantic', [])]:
    e = loc.get(x['id'], (None, None))[1]
    if e and sum(1 for t in e.get('vi_terms', []) if t.get('recommended')) != 1:
        bad += 1; print("  !! not exactly one recommended:", x['id'])

print('\n'.join(log))
print(f"\nFiles modified: {len(changed)} | switches: {sum(1 for l in log if l.startswith('  ✓'))} | integrity-bad: {bad}")
