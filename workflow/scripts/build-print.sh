#!/usr/bin/env bash
# Build the PDF with the designed cover embedded as page 1 and PreTeXt's title
# pages dropped — done INSIDE the LaTeX compile so cross-reference hyperlinks
# (named destinations) survive. Merging a separate cover PDF afterwards
# (pdfunite/qpdf/gs) strips the body's named destinations and breaks the links.
set -e
cd "$(dirname "$0")/../.."
PRETEXT="${PRETEXT:-$HOME/.venvs/pretext/bin/pretext}"
PYTHON="${PYTHON:-$HOME/.venvs/pretext/bin/python}"

# 0. Install the Vietnamese locale so structural labels (Chương, Định nghĩa, …)
#    render in Vietnamese; PreTeXt ships no vi locale. Idempotent.
bash workflow/scripts/install-vi-locale.sh

# 1. Recompile the cover. Stamp it with the release version (RELEASE_VERSION in
#    CI, e.g. 2026.06.25.1) or the build date (yyyy.mm.dd) for local builds.
printf '\\def\\coverversion{%s}\n' "${RELEASE_VERSION:-$(date +%Y.%m.%d)}" > assets/cover-version.tex
if command -v xelatex >/dev/null && [ -f assets/cover-front.tex ]; then
  ( cd assets && xelatex -interaction=batchmode cover-front.tex >/dev/null 2>&1 ) || \
    echo "WARNING: cover-front.tex recompile failed; using existing cover-front.pdf." >&2
fi
# Refresh the web cover image from the cover PDF (used by the web cover card).
command -v pdftoppm >/dev/null && [ -f assets/cover-front.pdf ] && \
  pdftoppm -png -r 150 -singlefile assets/cover-front.pdf assets/cover-front >/dev/null 2>&1 || true

# 1b. Regenerate the acknowledgements list (email contributors + any merged-PR
#     data already fetched into workflow/acknowledgements/merged-prs.json).
"$PYTHON" workflow/scripts/gen-acknowledgements.py

# 2. Generate LaTeX (no compile) so we can patch the preamble/title pages.
"$PRETEXT" build latex

# 3. Embed the cover (pdfpages) and drop the half-title + title page.
"$PYTHON" workflow/scripts/patch-cover-tex.py output/latex/main.tex

# 4. Compile the patched .tex (latexmk handles xelatex passes + makeindex).
( cd output/latex && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1 ) || \
  ( cd output/latex && latexmk -xelatex -interaction=nonstopmode main.tex >/dev/null 2>&1 ) || true

# 5. Publish to output/print/main.pdf.
mkdir -p output/print
if [ -f output/latex/main.pdf ]; then
  cp output/latex/main.pdf output/print/main.pdf
  echo "Built output/print/main.pdf ($(pdfinfo output/print/main.pdf | awk '/^Pages:/{print $2}') pages, cover embedded)"
else
  echo "ERROR: output/latex/main.pdf not produced." >&2
  exit 1
fi
