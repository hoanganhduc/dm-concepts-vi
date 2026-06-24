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

# 1. Recompile the cover so "Last Update: \today" reflects the current build date.
if command -v xelatex >/dev/null && [ -f assets/cover-front.tex ]; then
  ( cd assets && xelatex -interaction=batchmode cover-front.tex >/dev/null 2>&1 ) || \
    echo "WARNING: cover-front.tex recompile failed; using existing cover-front.pdf." >&2
fi

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
