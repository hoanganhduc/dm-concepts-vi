#!/usr/bin/env bash
# Emit the Codex review prompt for loop <i>. Usage: codex-review-prompt.sh <i>
i="${1:?usage: codex-review-prompt.sh <loop-number>}"
cat <<EOF
You are a meticulous bilingual (English-Vietnamese) discrete-mathematics dictionary reviewer.
Working directory: /home/ubuntu/DM-Concepts. Do NOT modify any file. Be evidence-based; never invent a translation or a source.

Read this batch of entries:
  cat workflow/loop/review/batch-${i}.json
It is a JSON array; each entry has: id, headword_en, definition_vi (Vietnamese), rosen_ref,
vi_terms (array of {term, source_id, page, pdf_page, verified, recommended}), see_ref.
If see_ref is non-empty the entry is a cross-reference stub: SKIP it.

For EACH non-stub entry, review THREE things line by line:

(1) CITATION ACCURACY. For each vi_term with verified=true whose source_id starts with 'bib-' and is one of the
LOCAL-TEXT sources below, verify the Vietnamese term actually appears in that source at/near the cited pdf_page:
    python3 workflow/scripts/find-term.py "<term>" <source_id> --loose
LOCAL-TEXT sources: bib-leanhvinh-2020 bib-nguyenhoangthach-2020 bib-nguyenhuudien-2019 bib-hoangchithanh-2007 bib-nguyenducnghia-2006 bib-ngodactan-2004 bib-rosen-2003-vi.
For any other source_id (e.g. bib-rosen-2019) there is no local text: mark 'no-corpus' and skip the check.
Report a citation_issue ONLY when find-term returns the term but NOT at/near the cited page, or returns ZERO hits for a verified term.

(2) TERM COMMONALITY. For the recommended Vietnamese term, judge whether it is the common/standard usage in Vietnamese.
Do a web search; prefer authoritative sources (Vietnamese university lecture notes, published textbooks, well-known references).
If the recommended term is uncommon and a clearly more standard term exists, report it WITH a source URL.

(3) ALTERNATIVE TRANSLATIONS. Find any additional valid Vietnamese translation of the English concept that is NOT already in vi_terms.
Example: 'independent set' = 'tập độc lập' AND 'tập ổn định' (internal stable set) - both should be present.
Use web search + authoritative sources. List each missing variant with a brief source.

Output ONLY entries that have at least one finding (skip clean entries). Print ONE JSON object on its own, then the final marker:
{"loop":${i},"reviewed":<int>,"findings":[{"id":"<id>","citation_issues":["..."],"commonality":{"verdict":"common|uncommon|unsure","better_term":"<term or empty>","sources":["url"]},"missing_variants":[{"term":"<vi term>","source":"<book or url>"}]}]}
===CODEX_REVIEW_DONE===

Keep the JSON valid (no comments, no trailing commas). Keep findings concise.
EOF
