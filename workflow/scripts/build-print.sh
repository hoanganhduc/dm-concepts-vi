#!/usr/bin/env bash
# Build the PDF and prepend the designed front cover.
# PreTeXt's <covers> does not embed the cover into the LaTeX/PDF output, so we
# build the body then prepend assets/cover-front.pdf as page 1 with pdfunite.
set -e
cd "$(dirname "$0")/../.."
PRETEXT="${PRETEXT:-$HOME/.venvs/pretext/bin/pretext}"
"$PRETEXT" build print
COVER=assets/cover-front.pdf
PDF=output/print/main.pdf
if [ -f "$COVER" ] && [ -f "$PDF" ]; then
  pdfunite "$COVER" "$PDF" /tmp/_main_cover.pdf && mv /tmp/_main_cover.pdf "$PDF"
  echo "Prepended cover -> $PDF ($(pdfinfo "$PDF" | awk '/^Pages:/{print $2}') pages)"
else
  echo "WARNING: cover or PDF missing; PDF has no designed cover." >&2
fi
