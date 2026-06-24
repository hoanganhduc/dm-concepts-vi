#!/usr/bin/env bash
# Build the PDF and prepend the designed front cover.
# PreTeXt's <covers> does not embed the cover into the LaTeX/PDF output, so we
# build the body then prepend assets/cover-front.pdf as page 1 with pdfunite.
set -e
cd "$(dirname "$0")/../.."
PRETEXT="${PRETEXT:-$HOME/.venvs/pretext/bin/pretext}"
# Recompile the cover so "Last Update: \today" reflects the current build date.
if command -v xelatex >/dev/null && [ -f assets/cover-front.tex ]; then
  ( cd assets && xelatex -interaction=batchmode cover-front.tex >/dev/null 2>&1 ) || \
    echo "WARNING: cover-front.tex recompile failed; using existing cover-front.pdf." >&2
fi
"$PRETEXT" build print
COVER=assets/cover-front.pdf
PDF=output/print/main.pdf
if [ -f "$COVER" ] && [ -f "$PDF" ]; then
  # PreTeXt page 1 = half-title, page 2 = title page — both redundant with the
  # designed cover. Drop them, then prepend the cover as the single front page.
  qpdf "$PDF" --pages . 3-z -- /tmp/_main_body.pdf && mv /tmp/_main_body.pdf "$PDF"
  pdfunite "$COVER" "$PDF" /tmp/_main_cover.pdf && mv /tmp/_main_cover.pdf "$PDF"
  echo "Dropped half-title/title pages, prepended cover -> $PDF ($(pdfinfo "$PDF" | awk '/^Pages:/{print $2}') pages)"
else
  echo "WARNING: cover or PDF missing; PDF has no designed cover." >&2
fi
