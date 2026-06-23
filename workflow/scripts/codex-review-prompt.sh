#!/usr/bin/env bash
# Emit the Codex web-review prompt for loop <i> (dimensions 2+3; dimension 1 is
# done deterministically by check-citations.py). Usage: codex-review-prompt.sh <i>
i="${1:?usage: codex-review-prompt.sh <loop-number>}"
cat <<EOF
You are a meticulous bilingual (English-Vietnamese) discrete-mathematics dictionary reviewer.
Working directory: /home/ubuntu/DM-Concepts. Do NOT modify any dictionary file. Be evidence-based; NEVER invent a translation or a source.

Read this batch of entries:
  cat workflow/loop/review/batch-${i}.json
It is a JSON array; each entry has: id, headword_en, definition_vi (Vietnamese), vi_terms (array of {term, recommended, ...}), see_ref.
If see_ref is non-empty the entry is a cross-reference stub: SKIP it.

For EACH non-stub entry, use WEB SEARCH (prefer authoritative Vietnamese sources: university lecture notes / giáo trình, published textbooks, standard references) to check TWO things:

(A) COMMONALITY of the recommended Vietnamese term (the vi_term with recommended=true): is it the common/standard rendering of this English concept in Vietnamese discrete mathematics? If it is uncommon and a clearly MORE standard term exists, report verdict "uncommon" with the better term and a source URL. Otherwise verdict "common" (or "unsure").

(B) ALTERNATIVE TRANSLATIONS: any additional valid Vietnamese translation of the English concept that is NOT already among the entry's existing vi_terms. Example: 'independent set' = 'tập độc lập' AND 'tập ổn định' (internal stable set). List each missing variant with a brief source (URL or book).

Efficiency (IMPORTANT - your context is limited): use web SEARCH RESULT SNIPPETS only; do NOT open or fetch full web pages or PDF files (fetching large pages overflows your context and the run fails). At most 1-2 lightweight searches per entry; skip entries that are clearly fine.

WRITE your result as a JSON file to workflow/loop/review/findings-${i}.json (use your file-writing tool), exactly this shape:
{"loop":${i},"reviewed":<int>,"findings":[{"id":"<id>","commonality":{"verdict":"common|uncommon|unsure","better_term":"<term or empty>","source":"<url or empty>"},"missing_variants":[{"term":"<vi term>","source":"<url or book>"}]}]}
Include ONLY entries that have at least one finding (an uncommon verdict OR a missing variant). Valid JSON only (no comments, no trailing commas).

After writing the file, print on its own line:  WROTE findings-${i}.json
Then print the final marker line:  ===CODEX_REVIEW_DONE===
EOF
