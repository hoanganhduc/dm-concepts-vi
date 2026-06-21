export const meta = {
  name: 'build-chapter',
  description: 'Build a verified lexicon chapter for args.letter: Rosen term-extract -> mine VI terms+pages across the 6-source corpus (recency-recommended, all variants) -> draft VI definitions -> adversarial verify -> editorial panel + synthesis. Applies the locked book conventions. Writes workflow/panels/chapter-<l>-final.json.',
  phases: [
    { title: 'Terms', detail: 'extract letter terms from Rosen' },
    { title: 'Mine+Draft', detail: 'mine VI terms+pages, draft VI definitions' },
    { title: 'Verify', detail: 'adversarially verify each entry' },
    { title: 'Panel', detail: 'editorial panel + synthesis' },
  ],
}

const LETTER = (args && args.letter ? String(args.letter) : 'G').toUpperCase()
const LOWER = LETTER.toLowerCase()
const COUNT = (args && args.count) ? args.count : 15
const SUGGEST = (args && args.suggest) ? args.suggest : ''
const REPO = '/home/ubuntu/DM-Concepts'

const SOURCES = [
  'Vietnamese corpus to mine (NEWEST first). The recommended term MUST be attested in a 2019-2020 source where possible, with its newest citations listed first:',
  '- bib-leanhvinh-2020 (2020, graph theory) [OCR -> ALSO try --loose]',
  '- bib-nguyenhoangthach-2020 (2020, combinatorics+graphs) [text]',
  '- bib-nguyenhuudien-2019 (2019, discrete math) [text]',
  '- bib-hoangchithanh-2007 (2007, graph algorithms) [OCR -> ALSO try --loose]',
  '- bib-nguyenducnghia-2006 (2006, discrete math+graphs) [text]',
  '- bib-ngodactan-2004 (2004, combinatorics+graphs) [text]',
  '(find-term.py already excludes the reference-only Rosen translation by default.)',
].join('\n')

const MINE = [
  'Mining tool (run from ' + REPO + '):',
  '  python3 workflow/scripts/find-term.py "<vietnamese term>" [biblio_id] [--loose]',
  'Returns {hits, results:[{source_id, pdf_page, snippet}]}. For OCR sources (bib-leanhvinh-2020, bib-hoangchithanh-2007) run BOTH normal and --loose (OCR mangles diacritics). Confirm via snippet that the term denotes THIS concept. Set page="tr. <pdf_page> (PDF)". NEVER fabricate a page or snippet.',
].join('\n')

const CONVENTIONS = [
  'LOCKED BOOK CONVENTIONS (apply to every entry):',
  '- Math: wrap EVERY inline math symbol in $$...$$ (e.g. $$G$$, $$K_n$$, $$\\chi(G)$$, set braces, gcd $$\\gcd(a,b)$$). Block math uses a ```math fence. No bare unwrapped math. Use $$\\geq$$ $$\\leq$$ $$\\neq$$, never ASCII >= <= !=.',
  '- Bipartite is rendered "đồ thị hai phần" (book standard); "đồ thị hai phía"/"đồ thị phân đôi" are listed variants only.',
  '- Exactly ONE vi_term has recommended=true; attested in a 2019-2020 source where possible; newest citations first. Still record EVERY variant from ALL sources (old+new). A recommended term may be verified=false only if NO source attests it (then explain in notes).',
  '- Citation hygiene: every verified=true vi_term carries source_id + pdf_page + snippet; drop verified=false + empty-page terms except one standard recommended term kept so vi_terms is non-empty.',
  '- Examples are self-contained (no derived quantity the definition did not introduce).',
  '- No synonym glosses inside the definition; variants live in vi_terms/notes.',
  '- see_also: kebab ids; only same-chapter ids get linked, cross-chapter are forward references.',
].join('\n')

const VITERM = {
  type: 'object',
  properties: {
    term: { type: 'string' }, source_id: { type: 'string' }, page: { type: 'string' },
    pdf_page: { type: 'integer' }, snippet: { type: 'string' },
    verified: { type: 'boolean' }, recommended: { type: 'boolean' },
  },
  required: ['term', 'verified', 'recommended'],
}
const ENTRY = {
  type: 'object',
  properties: {
    id: { type: 'string' }, letter: { type: 'string' }, headword_en: { type: 'string' },
    notation: { type: 'string' }, rosen_ref: { type: 'string' },
    definition_vi: { type: 'string' }, example_vi: { type: 'string' },
    vi_terms: { type: 'array', items: VITERM },
    see_also: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
  required: ['id', 'letter', 'headword_en', 'definition_vi', 'vi_terms'],
}
const TERMS_SCHEMA = {
  type: 'object',
  properties: {
    terms: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' }, headword_en: { type: 'string' }, notation: { type: 'string' },
          rosen_ref: { type: 'string' }, definition_en: { type: 'string' },
          vi_candidates: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'headword_en', 'definition_en', 'vi_candidates'],
      },
    },
  },
  required: ['terms'],
}
const VERDICT = {
  type: 'object',
  properties: { id: { type: 'string' }, ok: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } }, final_entry: ENTRY },
  required: ['id', 'ok', 'final_entry'],
}
const REVIEW = {
  type: 'object',
  properties: {
    dimension: { type: 'string' },
    findings: { type: 'array', items: { type: 'object', properties: { entry_id: { type: 'string' }, severity: { type: 'string' }, issue: { type: 'string' }, fix: { type: 'string' } }, required: ['entry_id', 'issue', 'fix'] } },
    chapter_notes: { type: 'array', items: { type: 'string' } },
  },
  required: ['dimension', 'findings'],
}
const SYNTH = {
  type: 'object',
  properties: { entries_written: { type: 'integer' }, summary: { type: 'string' } },
  required: ['summary'],
}

// ---- Phase 1: term list ----
phase('Terms')
const termList = await agent(
  'You are the Term Extractor for an English–Vietnamese discrete-mathematics lexicon based on Rosen, "Discrete Mathematics and Its Applications".\n' +
  'Produce ' + COUNT + ' entries whose English headword starts with "' + LETTER + '", prioritising graph-theory and combinatorics terms (the Vietnamese corpus is strongest there) but including key set/logic/number-theory terms too.\n' +
  (SUGGEST ? 'Suggested coverage (pick a balanced ' + COUNT + ', all genuinely starting with "' + LETTER + '"): ' + SUGGEST + '.\n' : '') +
  'For each: id (kebab-case, NO "def-" prefix), headword_en, notation (LaTeX, "" if none), rosen_ref (e.g. "Rosen §10.2"), a precise one-sentence English definition, and vi_candidates = 2-4 plausible Vietnamese translations to search for.\n' +
  SOURCES,
  { label: 'term-extract:' + LETTER, phase: 'Terms', schema: TERMS_SCHEMA }
)
const terms = (termList && termList.terms ? termList.terms : []).slice(0, COUNT)
log('Extracted ' + terms.length + ' ' + LETTER + '-terms')

// ---- Phase 2/3: mine -> draft -> verify (pipelined per term) ----
const verdicts = await pipeline(
  terms,
  (t) => agent(
    'You are the Vietnamese Term Miner for the lexicon entry "' + t.headword_en + '" (' + (t.notation || 'no notation') + ').\n' +
    'Concept (from Rosen): ' + t.definition_en + '\n' +
    'Candidate Vietnamese terms: ' + ((t.vi_candidates || []).join(', ')) + '.\n' +
    MINE + '\n' + SOURCES + '\n' + CONVENTIONS + '\n' +
    'Capture EVERY distinct Vietnamese term denoting THIS concept across ALL sources; each found with a real page gets verified=true with source_id, pdf_page, snippet, page. Mark exactly ONE recommended=true (standard term, attested in a 2019-2020 source where possible). If no source attests any candidate, keep one standard term verified=false/page="" and note it. Order vi_terms newest-source first.\n' +
    'Return the entry: id="' + t.id + '", letter="' + LETTER + '", headword_en, notation="' + (t.notation || '') + '", rosen_ref="' + (t.rosen_ref || '') + '", vi_terms, definition_vi="" (drafter fills next).',
    { label: 'mine:' + t.id, phase: 'Mine+Draft', schema: ENTRY }
  ),
  (entry, t) => agent(
    'You are the Definition Drafter for "' + t.headword_en + '".\n' +
    'English concept (ground truth): ' + t.definition_en + '\n' +
    CONVENTIONS + '\n' +
    'Vietnamese style: open with the term, state it formally and concisely, give notation with "ký hiệu"; 1-2 sentences; use the recommended Vietnamese term; do NOT invent terminology.\n' +
    'Entry so far (KEEP its vi_terms exactly): ' + JSON.stringify(entry) + '\n' +
    'Fill definition_vi (math wrapped in $$...$$), example_vi if natural (else ""), and see_also (kebab ids of related ' + LETTER + '-terms, or []). Return the COMPLETE entry.',
    { label: 'draft:' + t.id, phase: 'Mine+Draft', schema: ENTRY }
  ),
  (entry, t) => agent(
    'You are the Verifier (independent, adversarial) for "' + t.headword_en + '".\n' +
    'English concept (ground truth): ' + t.definition_en + '\n' +
    'Entry to check: ' + JSON.stringify(entry) + '\n' +
    MINE + '\n' + CONVENTIONS + '\n' +
    'Checks: (1) definition_vi faithful to the concept and well-formed Vietnamese with all math in $$...$$; (2) for each verified=true vi_term, re-run find-term.py (--loose for OCR sources) and confirm source_id/pdf_page and that the snippet denotes THIS concept, else set verified=false/page=""; (3) exactly one recommended=true, preferring a 2019-2020 source; (4) no fabricated citations.\n' +
    'Return ok, issues, and final_entry (corrected).',
    { label: 'verify:' + t.id, phase: 'Verify', schema: VERDICT }
  )
)

const entries = verdicts.filter(Boolean).map((v) => v.final_entry).filter(Boolean)
log(entries.length + ' entries verified')

// ---- Phase 4: editorial panel + synthesis ----
phase('Panel')
const dims = [
  { key: 'correctness', prompt: 'Review MATHEMATICAL correctness of every definition_vi against standard Rosen definitions. Flag wrong/imprecise ones.' },
  { key: 'terminology', prompt: 'Review Vietnamese TERMINOLOGY & CITATIONS: variant completeness, exactly one recommended (from newest source), verified citations backed by source_id+page, fabrication risk or concept mismatch.' },
  { key: 'exposition', prompt: 'Review Vietnamese PROSE/STYLE and consistency: all inline math in $$...$$, conventions honored, valid see_also, conciseness.' },
]
const reviews = await parallel(dims.map((d) => () => agent(
  'You are the ' + d.key + ' reviewer on the editorial panel for chapter ' + LETTER + ' of an EN–VI discrete-math lexicon.\n' +
  d.prompt + '\n' + CONVENTIONS + '\n' +
  'Entries: ' + JSON.stringify(entries) + '\n' +
  'Return dimension="' + d.key + '", findings (entry_id, severity high/med/low, issue, concrete fix), chapter_notes.',
  { label: 'panel:' + d.key, phase: 'Panel', schema: REVIEW }
)))

const synth = await agent(
  'You are the Editor/Synthesizer for chapter ' + LETTER + '. Apply the panel\'s clearly-correct fixes and produce the FINAL entries honoring all locked conventions.\n' +
  CONVENTIONS + '\n' +
  'Verified entries: ' + JSON.stringify(entries) + '\n' +
  'Panel findings: ' + JSON.stringify(reviews.filter(Boolean)) + '\n' +
  'Keep ALL entries; ensure exactly one recommended per entry (newest source); every verified=true vi_term keeps source_id+pdf_page+page+snippet; drop unverifiable non-recommended citations.\n' +
  'WRITE the result to ' + REPO + '/workflow/panels/chapter-' + LOWER + '-final.json as JSON {locked_conventions:[], deferred_note:"", final_entries:[...]} using your Write tool (create parent dirs). final_entries must use schema: id, letter, headword_en, notation, rosen_ref, definition_vi, example_vi, vi_terms[term,source_id,page,pdf_page,snippet,verified,recommended], see_also, notes.\n' +
  'Return entries_written (count) and a one-paragraph summary.',
  { label: 'panel:synthesize', phase: 'Panel', schema: SYNTH }
)

return { letter: LETTER, terms: terms.length, verified: entries.length, written: synth ? synth.entries_written : 0, summary: synth ? synth.summary : '' }
