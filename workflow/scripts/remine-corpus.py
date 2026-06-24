#!/usr/bin/env python3
"""Re-mine the whole book against the (expanded) corpus.

For every entry, search each existing vi_term string across all non-reference
corpus sources (diacritic-insensitive, OCR-tolerant). Two effects:

  1. Corroborating citations: when a term is attested in a source that the entry
     does not yet cite, add a verified vi_term citation (term unchanged).
  2. Recommended upgrade: when the recommended term is currently backed only by
     bib-rosen-2003-vi (reference-only) or is uncited, and the SAME term is now
     attested in a real published source, move the recommended flag onto the
     newest such cited instance (old kept as a variant).

Writes the panel final.json files in place; prints a report and writes
workflow/loop/review/remine-report.json. Confirmed term *choices* are preserved
— this only strengthens citations / re-points the backing of the same term.
"""
import glob, json, os, re, unicodedata, bisect, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "corpus")
PANELS = os.path.join(ROOT, "panels")
PAGE_RE = re.compile(r"@@PAGE (\d+)@@")
REFERENCE = {"bib-rosen-2003-vi"}
MIN_LEN = 6          # skip very short normalized terms (OCR noise)

# Printed-page offset per source: printed_page = pdf_page + offset. Only sources
# with a verified CONSTANT offset are listed; new citations from any other source
# are stored with an empty printed page (the book cites printed pages only, never
# the scan/PDF page). bib-phan-1976: cover=printed 1, offset 0 (verified). The
# 2004 dictionary has a non-constant offset (+4 then +5 across its two sections),
# so it is intentionally omitted -> page "" (cited without a page number).
PRINT_OFFSET = {"bib-phan-1976": 0}

# Only mine NEW sources for added citations, so a re-run corroborates with the
# freshly-added dictionaries without disturbing the existing, hand-curated
# (printed-page-verified) citations from sources already in the book.
NEW_SOURCES = {"bib-phan-1976", "bib-cungkimtien-2004"}

def strip(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()

# registry: source -> year (newest preferred when upgrading)
reg = yaml.safe_load(open(os.path.join(ROOT, "..", "data", "sources", "registry.yaml")))
YEAR = {s["biblio_id"]: (s.get("year") or 0) for s in reg["sources"]}

# load corpus blobs (non-reference only)
SRC = {}  # source_id -> (blob, starts[], pages[], raws[])
for f in sorted(glob.glob(os.path.join(CORPUS, "*.txt"))):
    sid = os.path.basename(f)[:-4]
    if sid in REFERENCE:
        continue
    pages, raws, norms = [], [], []
    page = 0
    for line in open(f, encoding="utf-8"):
        m = PAGE_RE.match(line.strip())
        if m:
            page = int(m.group(1)); continue
        pages.append(page); raws.append(line.rstrip("\n")); norms.append(strip(line))
    blob = "\n".join(norms)
    starts = []
    off = 0
    for n in norms:
        starts.append(off); off += len(n) + 1
    SRC[sid] = (blob, starts, pages, raws)
print(f"Loaded {len(SRC)} non-reference sources: {', '.join(sorted(SRC))}")

def find_in(sid, needle):
    """First WHOLE-WORD occurrence of needle. Plain substring matching gives
    false positives in a dense dictionary (e.g. 'lien ke' inside 'lien ket',
    'dinh ke' inside 'dinh kep'), so require non-alphanumeric boundaries."""
    blob, starts, pages, raws = SRC[sid]
    start = 0
    while True:
        idx = blob.find(needle, start)
        if idx < 0:
            return None
        before = blob[idx - 1] if idx > 0 else " "
        after = blob[idx + len(needle)] if idx + len(needle) < len(blob) else " "
        if not before.isalnum() and not after.isalnum():
            li = bisect.bisect_right(starts, idx) - 1
            return pages[li], " ".join(raws[li].split())[:200]
        start = idx + 1

# process entries
added = 0
upgraded = []
still_weak = []
loc, data = {}, {}
for f in sorted(glob.glob(os.path.join(PANELS, "chapter-*-final.json"))):
    d = json.load(open(f)); data[f] = d
    for e in d.get("final_entries", []):
        loc[e["id"]] = (f, e)

changed = set()
for eid, (f, e) in loc.items():
    if e.get("see_ref"):
        continue
    vts = e.get("vi_terms", [])
    have = {(t.get("source_id", ""), strip(t["term"])) for t in vts}
    # search every distinct term string
    terms = []
    for t in vts:
        if strip(t["term"]) not in [strip(x) for x in terms]:
            terms.append(t["term"])
    for term in terms:
        ns = strip(term)
        if len(ns) < MIN_LEN:
            continue
        for sid in NEW_SOURCES:
            if (sid, ns) in have:
                continue
            hit = find_in(sid, ns)
            if hit:
                page, snip = hit
                off = PRINT_OFFSET.get(sid)
                printed = f"tr. {page + off}" if off is not None else ""
                vts.append({"term": term, "source_id": sid, "page": printed,
                            "pdf_page": page, "snippet": snip, "verified": True,
                            "recommended": False})
                have.add((sid, ns)); added += 1; changed.add(f)
    # upgrade recommended if weak/uncited
    rec = next((t for t in vts if t.get("recommended")), None)
    if rec and (not rec.get("source_id") or rec.get("source_id") in REFERENCE):
        cands = [t for t in vts if t.get("verified") and t.get("source_id")
                 and t.get("source_id") not in REFERENCE and strip(t["term"]) == strip(rec["term"])]
        if cands:
            best = max(cands, key=lambda t: YEAR.get(t["source_id"], 0))
            for t in vts:
                t["recommended"] = False
            best["recommended"] = True
            upgraded.append({"id": eid, "term": best["term"], "from": rec.get("source_id") or "uncited",
                             "to": best["source_id"]})
            changed.add(f)
        else:
            still_weak.append({"id": eid, "term": rec["term"], "src": rec.get("source_id") or "uncited"})

for f in changed:
    json.dump(data[f], open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

os.makedirs(os.path.join(ROOT, "loop", "review"), exist_ok=True)
json.dump({"citations_added": added, "upgraded": upgraded, "still_weak": still_weak},
          open(os.path.join(ROOT, "loop", "review", "remine-report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"Citations added: {added}")
print(f"Recommended upgraded (weak/uncited -> real source): {len(upgraded)}")
print(f"Still weak/uncited recommended: {len(still_weak)}")
