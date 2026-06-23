#!/usr/bin/env python3
"""Classify recommended-term defects surfaced by the review into actionable
groups and emit docs/review-fixes-proposed.md. Read-only: writes the proposal
doc + a machine-readable repoint plan; applies nothing."""
import glob, yaml, json, unicodedata, re

def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

ent = {}
for f in sorted(glob.glob('data/terms/entries-*.yaml')):
    for e in (yaml.safe_load(open(f)) or {}).get('entries', []):
        ent[e['id']] = e

REPOINT, TERMCHG, WEAK, NOISE = [], [], [], []
for e in ent.values():
    if e.get('see_ref'):
        continue
    vts = e.get('vi_terms', []) or []
    rec = next((t for t in vts if t.get('recommended')), None)
    if not rec:
        continue
    rsrc, rterm = rec.get('source_id'), rec['term']
    weak, uncited = (rsrc == 'bib-rosen-2003-vi'), (not rsrc)
    if not (weak or uncited):
        continue
    real = [t for t in vts if t.get('verified') and t.get('source_id')
            and t.get('source_id') != 'bib-rosen-2003-vi']
    same = [t for t in real if norm(t['term']) == norm(rterm)]
    if same:
        REPOINT.append({'id': e['id'], 'term': rterm, 'source_id': same[0]['source_id']})
    elif real:
        cn = norm(real[0]['term']); rn = norm(rterm)
        if cn and cn in rn and len(cn.split()) < len(rn.split()):
            NOISE.append((e['id'], rterm, real[0]['term']))
        else:
            TERMCHG.append((e['id'], rterm, 'Rosen-2003' if weak else 'uncited',
                            [(t['term'], t['source_id']) for t in real[:3]]))
    elif weak:
        WEAK.append((e['id'], rterm))

# Curated, hand-verified semantic / clear-improvement switches (editor-approved set)
SEMANTIC = [
    ('geodesic', 'khoảng cách', 'đường đi ngắn nhất', 'bib-nguyenhuudien-2019',
     'Headword là *shortest path*; "khoảng cách" = độ dài (distance). Biến thể có trích dẫn khớp khái niệm.'),
    ('conditional-statement', 'Cấu trúc điều kiện', 'Phép kéo theo', 'bib-nguyenhuudien-2019',
     '"Cấu trúc điều kiện" là dịch máy (giống lập trình); dùng biến thể có trích dẫn nguồn-thật gần nghĩa nhất.'),
]

lines = []
W = lines.append
W('# Đề xuất sửa từ kết quả review\n')
W('Review (Codex 20 batch + audit toàn cục) phát hiện thuật ngữ **recommended** không tuân thủ '
  'chính sách "recommended phải là thuật ngữ có trích dẫn từ nguồn không-phải-tham-khảo, ưu tiên nguồn mới". '
  'Các mục được chia 4 nhóm theo rủi ro.\n')

W(f'## Nhóm 1 — RE-POINT ({len(REPOINT)}): cùng thuật ngữ, chỉ gắn lại trích dẫn (AN TOÀN)\n')
W('Thuật ngữ recommended **không đổi**; chỉ chuyển nhãn recommended sang một trích dẫn từ nguồn '
  'không-phải-Rosen-2003 đã có sẵn trong mục. Khuyến nghị: **áp dụng tự động**.\n')
W('| id | thuật ngữ (giữ nguyên) | gắn trích dẫn |')
W('|---|---|---|')
for x in REPOINT:
    W(f"| {x['id']} | {x['term']} | {x['source_id']} |")
W('')

W(f'## Nhóm 2 — SỬA NGỮ NGHĨA / cải thiện rõ ràng ({len(SEMANTIC)}): đã xác minh thủ công\n')
W('| id | recommended hiện tại | đổi thành | trích dẫn | lý do |')
W('|---|---|---|---|---|')
for i, t, n, s, r in SEMANTIC:
    W(f"| {i} | {t} | **{n}** | {s} | {r} |")
W('')

W(f'## Nhóm 3 — ĐỔI THUẬT NGỮ ({len(TERMCHG)}): cần bạn duyệt từng mục\n')
W('Recommended hiện tại khác mọi biến thể có trích dẫn. Một số là dịch máy nên thay; một số '
  'ứng viên lại **sai/hẹp nghĩa** (vd `propositional-function` "hàm mệnh đề" vs ứng viên "vị từ"=predicate). '
  'KHÔNG áp dụng hàng loạt.\n')
W('| id | recommended hiện tại | nguồn gốc | ứng viên có trích dẫn |')
W('|---|---|---|---|')
for i, t, kind, cands in TERMCHG:
    cs = '; '.join(f"{c[0]} ({c[1]})" for c in cands)
    W(f"| {i} | {t} | {kind} | {cs} |")
W('')

W(f'## Nhóm 4 — WEAK-CITATION ({len(WEAK)}): thuật ngữ ổn nhưng chỉ Rosen-2003 trích\n')
W('Thuật ngữ recommended đúng và phổ biến, nhưng trong corpus chỉ có Rosen-2003-vi (tham khảo) trích. '
  'Lựa chọn: (a) re-mine corpus tìm nguồn mới hơn, hoặc (b) chấp nhận giữ "cách dùng" không trích dẫn. Ưu tiên thấp.\n')
W('> ' + ', '.join(x[0] for x in WEAK) + '\n')

W(f'## Nhóm 5 — NOISE ({len(NOISE)}): gợi ý mất chữ/đầu ngữ — GIỮ NGUYÊN\n')
W('Ứng viên Codex là dạng cụt của thuật ngữ hiện tại (vd `independent-events`: "biến cố độc lập" '
  'vs gợi ý "biến cố"). Không sửa.\n')

open('docs/review-fixes-proposed.md', 'w', encoding='utf-8').write('\n'.join(lines))

# machine-readable plan for the safe set
json.dump({'repoint': REPOINT, 'semantic': [
    {'id': i, 'from': t, 'to': n, 'source_id': s} for i, t, n, s, _ in SEMANTIC]},
    open('workflow/loop/review/fix-plan.json', 'w', encoding='utf-8'),
    ensure_ascii=False, indent=1)

print(f"RE-POINT={len(REPOINT)}  SEMANTIC={len(SEMANTIC)}  TERM-CHANGE={len(TERMCHG)}  "
      f"WEAK={len(WEAK)}  NOISE={len(NOISE)}")
print("wrote docs/review-fixes-proposed.md and workflow/loop/review/fix-plan.json")
