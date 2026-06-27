# Translation-review methodology (multi-agent + independent verification)

How the Vietnamese translations in this book are reviewed for accuracy. Three
complementary methods, all built on one rule: **never trust an agent's finding;
verify it independently against the real entry, the cited source, and known
conventions before accepting it.** This document is the reusable playbook.

## Reviewers (external CLIs)

Three different model families, dispatched read-only. Probe each before a run
(auth + file-read + output). Exact non-interactive invocations:

| Reviewer | Invocation | Model family |
|---|---|---|
| Codex | `codex exec -s read-only --skip-git-repo-check "<prompt>" < /dev/null` | OpenAI |
| OpenCode | `opencode run "<prompt>" < /dev/null` | Gemini |
| CodeWhale | `codewhale exec --auto "<prompt>" < /dev/null` | DeepSeek |

Gotchas: `--skip-git-repo-check` (Codex needs a trusted/git dir); `--auto`
(CodeWhale needs it for file/tool access — plain `exec` is a one-shot reply);
`< /dev/null` on all (they block reading stdin in the background otherwise).
Reviewers run with `cwd` = a **read-only copy** of `data/terms/` + `registry.yaml`
+ `references.ptx` so they cannot touch the repo. Capture stdout to a file.

## Scratch infrastructure (`/tmp/dm-review/`, ephemeral — recreate each run)

`dispatch.sh` — uniform dispatch (paths relative to `/tmp/dm-review`):

```bash
#!/usr/bin/env bash
# dispatch.sh <agent> <promptfile> <outfile>
agent="$1"; promptfile="$2"; out="$3"
case "$promptfile" in /*) ;; *) promptfile="/tmp/dm-review/$promptfile";; esac
case "$out" in /*) ;; *) out="/tmp/dm-review/$out";; esac
P="$(cat "$promptfile")" || exit 2
cd /tmp/dm-review/book || exit 2
{ case "$agent" in
  codex)     timeout 1500 codex exec -s read-only --skip-git-repo-check "$P" < /dev/null ;;
  opencode)  timeout 1500 opencode run "$P" < /dev/null ;;
  codewhale) timeout 1500 codewhale exec --auto "$P" < /dev/null ;;
esac ; } > "$out" 2>&1
```

`extract.py` — pull the findings JSON out of an agent's (noisy/ANSI) stdout.
Agents often emit a **bare JSON array at the end** without the requested
markers, so try the marker block first, then fall back to the **last** valid
JSON array of dicts:

```python
import sys, re, json
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
raw = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b[()][AB0]", "", raw)  # strip ANSI/OSC
m = re.search(r"<<<FINDINGS_JSON(.*?)FINDINGS_JSON>>>", raw, re.S)
if m:
    seg = m.group(1); a, b = seg.find("["), seg.rfind("]")
    try: print(json.dumps(json.loads(seg[a:b+1]), ensure_ascii=False)); sys.exit(0)
    except Exception: pass
ends=[i for i,c in enumerate(raw) if c=="]"]; starts=[i for i,c in enumerate(raw) if c=="["]
for rb in reversed(ends):
    for lb in reversed([s for s in starts if s < rb]):
        try:
            v=json.loads(raw[lb:rb+1])
            if isinstance(v,list) and v and isinstance(v[0],dict) and "entry_id" in v[0]:
                print(json.dumps(v,ensure_ascii=False)); sys.exit(0)
        except Exception: continue
print("[]")
```

Ledger per run: `iterations.jsonl` (one record per loop) + `loopN-confirmed.md`
(Claude's verified verdicts). Keep a separate dir per run (`run2/`, etc.).

---

## Method A — Multi-agent angle review (5 loops)

Each loop = one **distinct angle**; all three reviewers run it in parallel; the
prompt forces a **JSON-only** output. Claude then verifies every finding.

The five angles (each loop's prompt says "do NOT re-report prior angles"):

1. **Recommended-term correctness** — is the recommended Vietnamese term the
   correct/standard translation of the English headword for its specific sense?
2. **Definition accuracy & completeness** — is `definition_vi` (and `example_vi`)
   mathematically correct, complete, non-circular? wrong/contradictory examples.
3. **Citation/source integrity** — does the recommended term's `snippet` actually
   contain the term? snippet/term/page/source mismatches.
4. **Semantic precision & concept conflation** — wrong-sense translations,
   conflated distinct concepts (maximal vs maximum, walk vs path), POS errors.
5. **Cross-cutting consistency** — same English term translated inconsistently;
   one Vietnamese term reused for different English concepts; see_also/notation.

Strict prompt template (the JSON contract is essential — without it Codex emits
hundreds of KB of prose and OpenCode wanders):

```
You are an expert reviewer of bilingual English–Vietnamese math & CS terminology.
The cwd holds a READ-ONLY copy: ./data/terms/entries-<letter>.yaml (data model in
./README-FOR-REVIEWER.md). Do NOT modify any file. Scan broadly; report only
clear-cut, confident findings (max ~12), precision over recall, each with a
specific entry id and a concrete reason.

REVIEW ANGLE — <angle text>.

CRITICAL OUTPUT RULES:
- Do NOT review entries one-by-one in prose. Scan, then report ONLY clear errors.
- Your ENTIRE answer must be ONLY a JSON array (max 8), nothing before/after, no fences.
- Each: {"entry_id","headword_en","current_term","issue","why","severity","suggested_fix"}
- If none, output exactly: []
```

Per loop: dispatch 3 agents in parallel → `extract.py` each → **Claude verifies
each finding against the real repo** (the actual YAML, the cited source/corpus,
domain knowledge, Rosen's conventions) → keep only confirmed → record. After
loop 5, aggregate deduplicated verified errors.

## Method B — Back-translation grounding (context-faithful citation check)

The deepest check: does the Vietnamese term, **as used in its cited source**,
actually mean the English headword *in context*?

1. Build candidates: entries whose recommended term is `verified` with a
   `source_id` + `snippet`; extract a context window from
   `workflow/corpus/<source_id>.txt` (strip `@@PAGE n@@`) around the snippet.
2. **Translator agent (blind)** — given `{id, vi_term, context}` (NO English
   headword), translate the context to English faithfully. Output `[{id, en}]`.
3. **Checker agent (different agent)** — given `{id, en_headword, vi_term,
   en_translation}`, judge whether **in context** the Vietnamese term is used
   with the English headword's meaning: `match | mismatch | unclear` + reason.
4. **Claude verifies** every `mismatch`/`unclear` against the real source.

"Match" = contextually correct (not just a literal string match). Translator
must be blind to the English headword to avoid confirmation bias; checker ≠
translator. ~40 entries/loop is a workable batch for one agent call.

**Checker prompt must be synonym-aware** (learned in Run 3, loop 1). A literal
checker over-reports: the source is Vietnamese, so the back-translation almost
never contains the exact English headword, and a strict checker calls every
paraphrase a `mismatch`. Tell the checker explicitly: *the source is Vietnamese
text, so the translation usually will NOT contain the exact English term; if the
context describes the SAME CONCEPT with a synonym or different wording it is
still `match`* — with concrete pairs: `shortest path`=geodesic; `unrooted
tree`=free tree; `predicate logic`=first-order logic; `length of the shortest
cycle`=girth. Only `mismatch` when the context is about a GENUINELY DIFFERENT
concept. Without this, loop 1 produced 5 false synonym-mismatches and 0 real
errors; with it, loops 2–5 surfaced 5 real fold-homograph citations + 1 term
error and almost no synonym noise.

**Operational gotchas (Run 3):**
- *Build the translator/checker prompt file BEFORE dispatching* — a `dispatch.sh
  ... &` that races ahead of the `python` writing its prompt file `cat`s an empty
  file. Sequence: write prompt → then dispatch.
- *`dispatch.sh` lives in `/tmp/dm-review/`, not in `backtrans/`.* Run dispatch
  from `/tmp/dm-review` (paths like `backtrans/loopN-*.prompt`), not from inside
  `backtrans/`, or `bash dispatch.sh` is "No such file or directory".
- *OpenCode (Gemini) buffers ALL stdout to the end and sometimes stalls* — the
  output file sits at the ~56-byte startup banner for 8+ minutes with no
  progress. If it has not produced the JSON array after ~8 min, kill it and
  re-dispatch the SAME prompt on CodeWhale (reliable for the checker role).
- *Never `pkill -f "opencode run"` / `pkill -f "codewhale exec"` from a shell
  whose own command line contains that string* — `pkill -f` matches your current
  bash process and SIGTERMs it (exit 144). Kill by basename instead:
  `for p in $(ps -eo pid,comm | awk '$2=="opencode"{print $1}'); do kill $p; done`.
- *Translators (Codex) and the next loop's checker are different model families*
  — dispatch loop N+1's translator in parallel with loop N's checker to overlap
  wall-clock.

---

## Verification discipline & known FALSE-POSITIVE patterns

Independent verification routinely overturns ~40–60% of agent findings. Watch
for these recurring false positives (confirmed across two full runs):

- **see-ref stubs flagged as "empty definition" / "empty entry".** Entries with
  a `see_ref` field are redirects ("Xem <target>") and are empty BY DESIGN
  (`range`→`range-of-a-function`, `np-complete`→`np-complete-problem`, etc.).
  Adding a definition would duplicate the target. ~11 of these per run.
- **`mapping-rule`** ("quy tắc song ánh") is flagged almost every run as needing
  "quy tắc ánh xạ" — it is the **bijection rule** (deliberately unified), correct.
- **Rosen-convention vs standard-convention.** The book follows Rosen: "path" =
  walk, "simple path" = no repeated edge, "circuit" allows repeated vertices,
  "decreasing" = non-strict. Agents applying the other convention raise false
  alarms (but Run 2 correctly caught that **`decreasing` had Rosen backwards** —
  verify the convention, don't assume).
- **Umbrella/disambiguation entries** (`inverse`, `complement`, `root` has
  several senses) have intentionally general definitions ("Mục này chỉ nêu ý
  niệm chung") — not "circular/vague" errors.
- **Real-but-obscure cited terms** called "hallucinated": e.g. `literal`="tục
  biến" (18 corpus hits, Đỗ Đức Giáo 2000), `implicant`="nguyên nhân". Check the
  corpus before rejecting a term as invented.
- **Citation checks need OCR/diacritic tolerance.** "snippet doesn't contain the
  term" is usually false — fold diacritics + case before comparing. BUT the
  inverse trap is real: a **fold-homograph** (different word, same folded form)
  is a genuinely spurious citation — `gate`"cổng"←"công việc", `even`"chẵn"←"Chặn
  trên", `centre`"tâm"←"Tam giác". Check exact-vs-folded; ToC/heading/preface
  snippets are high-risk. Back-translation (Method B) is the strongest detector
  of these — it reads the actual surrounding passage, so it catches **word-break
  folds** the term never spanned: `resolution`"hợp giải"←"tập **hợp giải** tích"
  (analytic set), `witness`"bằng chứng"←"bằng **chứng minh**" (by the proof),
  `double-sum`"tổng đôi"←"tổng **đối thớ**" (cofibered sum) / "tổng **đối** với
  tích" (distributive). Also **wrong-sense** folds where the word matches but the
  meaning differs: `pivot`"chốt"←"đặt **chốt** bảo vệ" (guard post, not the
  algorithm pivot), `proof-by-contraposition`"chứng minh phản đảo"←"chứng minh
  **phần đảo**" (prove the converse part, in a Boolean-algebra exercise).
- **Established subfield terms** that look like conflations but aren't:
  `maximum-flow`="luồng cực đại", `xnor`="phép tương đương" (XNOR = logical
  equivalence), `ball`="hình cầu" (solid ball; sphere surface = "mặt cầu").

Also catch **residuals from your own term fixes**: changing a recommended term
without updating the definition/example leaves the old term in the prose
(`codomain` def kept "miền giá trị", `contingency` kept "tiếp liên",
`linear-recurrence` kept "thuần nhất"). After any term change, re-check the
definition opener and example.

## Run history (for reference)

- **Run 1** (full book): ~90 raw findings → ~35 verified errors fixed; ~45 false
  positives rejected. Fixed: permutation, existential→"hiện sinh" (left per
  author), codomain term, prime-implicant reversed implication, dynamic-
  programming Dijkstra example, broken see_also (headword strings → ids), etc.
- **Run 2** (re-run, current book): ~11 verified, mostly **residual def/term
  mismatches from Run 1's fixes** + new (root, series, discrete, class-P,
  6 fold-homograph spurious citations). Validates re-running.
- **Run 3** (Method B — back-translation, 5 loops × 40 = 200 entries): 190
  confirmed correct in context; **6 verified issues** — 1 term error
  (`double-sum`: recommended "tổng đôi" had no valid citation, all 4 were folds
  of "tổng đôi **một**"/"tổng **đối** thớ"; the correctly-cited "tổng kép",
  Rosen VI tr.100, was `recommended:False` → swap) + 5 spurious citations
  (`pivot`, `proof-by-contraposition`, `resolution`, `witness`, plus the
  double-sum cites). Loop 1's literal checker gave 5 false synonym-mismatches
  and 0 real errors → fixed by the synonym-aware prompt. Lesson: back-translation
  finds citation-integrity defects the angle review (Method A) misses, because it
  reads the source passage, not just the snippet.
- The **existential-instantiation/generalization "hiện sinh"** pair is left
  unchanged by author request — do not "fix" it.

## Method C — Scripted cross-entry / corpus gap-checks (read-only)

Three deterministic reports that catch defect classes the per-entry validation
and the LLM review cannot see, because they are *relations between* entries or
*frequency* facts. None changes the book; each prints a summary and writes a
JSON report under `workflow/loop/review/`. They came out of a deep-research +
multi-agent gap analysis (the unused-measures audit; see
`workflow/loop/review/*-report.json`). The full catalog of verification methods,
what the repo already does, and the prioritized list of measures still unused
(Tier A #4–#8, plus the demoted/covered ones) is in the
*Method catalog & gap analysis* section at the end of this document.

- **`consistency-report.py`** — bilingual consistency cross-tabs. (A) same
  *recommended* VI term used for >1 distinct EN headword (homonym collision;
  most are legit synonyms — review each); (B) same EN headword across entries
  recommending divergent VI. Found real cross-entry slips the per-entry passes
  missed (e.g. `tiên đề` recommended for both *axiom* and *premise*; `khoảng`
  for both *interval* and *open interval*).
- **`variant-frequency.py`** — corpus frequency *dominance*. Existing mining
  proves a variant is *attested*; this counts whole-token occurrences across the
  corpus (fast one-pass n-gram model; rosen-2003-vi excluded) and flags entries
  where the recommended term is out-frequented by a **comparable** variant
  (within 1 token, not a fragment — the length filter is essential, else lone
  generic words like `tập` swamp precise multi-word terms) or has 0 hits while a
  variant has some. Surfaces dominance candidates (e.g. `truth value`
  `giá trị chân trị`(3) vs `giá trị chân lý`(173)). Heuristic — a review aid.
- **`rosen-coverage.py`** — headword recall vs the Rosen gold list
  (`data/rosen-master.json`, 319 terms; `--gold data/rosen-key-terms.json` for
  the 339 chapter key-terms). Normalized exact + whole-word fuzzy match; reports
  recall and the missing terms. Result: 318/319 exact (99.7%), 100% with fuzzy —
  full coverage of the Rosen master list.

## How to re-run

1. `mkdir -p /tmp/dm-review/{book/data/terms,book/data/sources,results}`; copy
   `data/terms/*.yaml`, `data/sources/registry.yaml`, `source/references.ptx`
   into `book/`; write `book/README-FOR-REVIEWER.md` (the data model). Recreate
   `dispatch.sh` + `extract.py` (above).
2. Probe the three CLIs (short file-read prompt).
3. For each angle: dispatch 3 agents in parallel → extract → Claude verifies →
   record → next loop. Aggregate after loop 5, then apply fixes (panels →
   `encode-chapter.py` → `validate-entry.py` → build → commit).
4. For Method B: build candidates with corpus context, then translator → checker
   → Claude verifies mismatches.

---

# Method catalog & gap analysis

The wider landscape behind Methods A/B/C: every method that exists for verifying
a bilingual term lexicon, which ones the repo already applies, and which remain
unused — with a priority for the unused ones.

Produced by a deep-research + multi-agent gap analysis: four parallel
web-grounded research agents (translation-QA frameworks / lexicography &
terminography / MT-evaluation & tooling / empirical-panel & corpus-statistics)
→ a multi-agent discussion (Repo-grounder → Synthesizer → Skeptic → Referee).

**Hard rule carried throughout:** a measure counts as "unused" only if a repo
audit confirms no equivalent already exists, and **frequency ≠ correctness** —
every candidate defect is verified against the real entry/citation before
acting. Independent verification routinely overturns flagged candidates (it
caught that a "consistency error" was a bug in the checker script, and that most
frequency outliers were correct deliberate choices).

> Sourcing caveat: the ISO / MQM / SAE primary texts are paywalled; framework
> names and criteria below come from the standards' free scope pages and
> reputable secondary summaries (W3C MQM CG, Wikipedia, NORDTERM, ACL/WMT
> papers, vendor docs). Verify exact clause wording against the purchased
> standard before quoting it as normative.

## Baseline: what the repo already does

- **Methods A / B / C** above (multi-agent angle review, back-translation
  grounding, scripted gap-checks).
- **Corpus citation verification with page-match** — `check-citations.py`.
- **Corpus citation mining / re-mining** — `find-term.py`, `remine-corpus.py`.
- **Course-terminology cross-check** — `audit-mat3500.py` vs MAT3500 pairs.
- **Structural build-gate** — `validate-entry.py` in CI.
- **Bilingual search index** — `build-search-index.py`.
- **Panel-approval gates + documented SOP** (this file, the false-positive
  pattern library, run history).

## The catalog

Status legend: **DONE** = implemented · **PARTIAL** = a related mechanism exists ·
**PENDING** = unused, recommended · **DEMOTE** = unused, low value here ·
**COVERED** = effectively already done by another mechanism.

### Translation-QA frameworks

| Method | Framework / source | Catches | Repo status |
|---|---|---|---|
| Severity-weighted scoring + numeric release gate | MQM / LISA QA / DQF | unprioritized findings; no pass/fail threshold | **PENDING** (HIGH/MED/LOW in prose only, not per-entry/gated) |
| Fixed error typology (tag set) | MQM Core, SAE J2450 | un-countable, un-trendable findings | DEMOTE (MT-production scale) |
| Monolingual "review" pass (≠ bilingual revision) | EN 15038 / ISO 17100 | VI fluency/register defects invisible to EN-anchored review | **PENDING** (high value) |
| Up-front translation specification | ISO 11669 / ASTM F2575 | implicit, taste-based judging | PARTIAL (registry has term-authority/recency; no audience/register) |
| Recorded second-person revision sign-off | ISO 17100 | no attributable per-entry audit trail | DEMOTE (provenance, not defect-catching) |

### Lexicography / terminography

| Method | Framework / source | Catches | Repo status |
|---|---|---|---|
| Definition-adequacy tests (genus–differentia, non-circularity, substitutability, scope) | ISO 704; Suonuuti, NORDTERM | circular/too-wide/too-narrow defs; non-substitutable def | **PENDING** (non-circularity scriptable; rest on LLM harness) |
| ISO 704 term-formation scoring | ISO 704 | opaque/over-long/loanword recommended terms | DEMOTE (~0 yield on curated entries) |
| Defining-vocabulary closure | Suonuuti | a def's technical term that is neither a headword nor general-language | DEMOTE (learner-dictionary instrument) |
| Concept-system / onomasiological coverage map | ISO 1087 | missing siblings (BFS but no DFS), duplicate concepts | DEMOTE→optional (graph over `see_also`) |
| preferred / admitted / **deprecated** status model | ISO 10241 | usable synonym vs discouraged variant collapsed into one bucket | DEMOTE (binary `recommended` today) |
| full / partial / **zero** equivalence tag | ISO 12616; Gouws/Wiegand | a confident 1:1 VI term where equivalence is only partial/none | **PENDING** (real risk for a math lexicon) |
| External dictionary-criticism review (Nielsen) | metalexicography (IJL, Lexikos) | whole-work structural/function defects | DEMOTE (blocked: no external reviewer) |
| Information-cost / readability of definitions | Nielsen | unfindable / over-dense defs | DEMOTE (VI readability formulas unreliable) |

### MT-evaluation & terminology tooling

| Method | Framework / source | Catches | Repo status |
|---|---|---|---|
| Bilingual consistency cross-tabs | WMT *Term Consistency*; Xbench / QA-Distiller | one VI term for two EN concepts; one EN with conflicting VI | **DONE** (`consistency-report.py`) |
| Variant frequency dominance | corpus keyness (Scott, WordSmith) | recommended term attested but not the *dominant* usage | **DONE** (`variant-frequency.py`) |
| Rule-based mechanical QA (VI spelling/grammar/spacing) | LanguageTool, Translate-Toolkit `pofilter`, Okapi CheckMate | typos / double-spaces / punctuation | DEMOTE (LanguageTool VI module thin) |
| Second independent MT-engine cross-check | QE-by-divergence (CometKiwi) | entries where a fresh engine's VI term diverges | **COVERED** (3-engine LLM panel + back-translation) |
| Reference-based metrics (BLEU, chrF, METEOR, TER) | Papineni 2002; Popović 2015 | surface n-gram divergence vs a reference | DEMOTE (need references; meaningless on term pairs) |
| Reference-free QE (COMET-QE / CometKiwi) | Rei et al. 2022 | low-confidence entries, no reference | DEMOTE→optional (sentence-trained triage only) |
| Inter-annotator agreement (κ, Krippendorff α) | Artstein & Poesio 2008 | whether human/LLM verdicts are reproducible | DEMOTE (measures process, not correctness) |

### Empirical / panel / corpus-statistical

| Method | Framework / source | Catches | Repo status |
|---|---|---|---|
| Headword coverage / recall vs an authoritative list | precision/recall (Powers); Rosen index | missing high-frequency domain terms | **DONE** (`rosen-coverage.py`: 318/319 exact) |
| Acceptance / attribute sampling + error rate + CI | ISO 2859 | book-wide error-rate estimate vs ad-hoc review | **PENDING** (best effort-to-evidence ratio) |
| Cross-check vs national VN terminology dictionaries | ISO 10241-2 / 12616 | divergence from established equivalents | PARTIAL (Cung Kim Tiến dict in corpus; `audit-mat3500.py`) |
| External expert panel / Delphi / Content-Validity-Index | ISO 704; Lynn 1986, Polit & Beck 2006 | arbitrary recommended choices; quantified SME validity | DEMOTE (blocked: needs human experts) |
| Reader / look-up usability testing | metalexicography "dictionary use" | entries correct but unusable in a look-up | DEMOTE (needs human subjects) |
| Corpus keyness / salience | log-likelihood keyness (Rayson) | headwords not actually salient domain terms | DEMOTE→optional (needs domain+reference corpus) |
| Diachronic / neologism attestation | monitor-corpus neology (Neoveille) | unstable coinages/calques | DEMOTE (low priority for a stable vocabulary) |

## Unused measures — prioritized

**Tier A — worth doing (unused, high-value, solo-feasible):**
1. Bilingual consistency cross-tabs — **DONE** (`consistency-report.py`).
2. Variant frequency dominance — **DONE** (`variant-frequency.py`).
3. Headword recall vs Rosen — **DONE** (`rosen-coverage.py`).
4. **VI-only monolingual review pass** — PENDING. LLM pass over the VI
   definition/example with the English hidden; catches register/fluency defects
   the EN-anchored review is blind to.
5. **Definition non-circularity + adequacy tests** — PENDING. Non-circularity
   scriptable; genus-differentia/substitutability on the LLM harness.
6. **Acceptance sampling + measured error rate + CI** — PENDING. Random sample →
   book-wide error-rate estimate with a confidence interval.
7. **full / partial / zero equivalence tag** — PENDING. Schema field flagging EN
   terms with no true VI equivalent (calque-only).
8. **Severity field + numeric release gate** — PENDING (extend). Record
   HIGH/MED/LOW per-entry; block release on unresolved HIGH.

**Tier B — demote (low value here / impractical):** preferred/admitted/deprecated
status model · concept-system map · LanguageTool/pofilter · κ/α statistics ·
ISO 704 term-formation scoring · defining-vocabulary closure · MQM/J2450 tagging ·
readability/information-cost · BLEU/METEOR/TER family · external panel/Delphi/CVI ·
usability testing · keyness salience · neologism tracking.

**Tier C — already covered / only partial (do NOT call fully unused):** second MT
engine (covered by the 3-engine panel + back-translation) · VN-dictionary
cross-check (partial: Cung Kim Tiến + `audit-mat3500.py`) · written spec (partial:
registry policy) · coverage tooling (the Rosen *recall metric* was the gap, now
DONE; `extract-rosen-terms.py` already built the gold list).

## Outcome so far

Tier A #1–#3 are Method C. Running them produced two verified, approved content
fixes: `open interval` recommended `khoảng` → `khoảng mở`; `truth value`
`giá trị chân trị` → `giá trị chân lý`. Most flagged candidates were verified
correct and left unchanged. Tier A #4–#8 remain available as the next increment.
