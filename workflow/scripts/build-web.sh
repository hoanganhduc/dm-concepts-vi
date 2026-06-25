#!/usr/bin/env bash
# Build the web target into output/web, ready to publish to gh-pages:
#   regenerate the acknowledgements list, build HTML, build the quick-lookup
#   search index, bundle the lookup page, and post-process channel icons.
# Used by both local builds and the CI build-deploy job so the two never drift.
set -e
cd "$(dirname "$0")/../.."
PRETEXT="${PRETEXT:-$HOME/.venvs/pretext/bin/pretext}"
PYTHON="${PYTHON:-$HOME/.venvs/pretext/bin/python}"
command -v pretext >/dev/null 2>&1 && PRETEXT="$(command -v pretext)"
command -v python3 >/dev/null 2>&1 && PYTHON="${PYTHON:-python3}"

# 0. Vietnamese structural labels (idempotent; also fetches PreTeXt core).
bash workflow/scripts/install-vi-locale.sh

# 1. Acknowledgements list (email contributors + any merged-PR data already
#    fetched into workflow/acknowledgements/merged-prs.json).
"$PYTHON" workflow/scripts/gen-acknowledgements.py

# 2. Build HTML. Clean output/web first so removed pages (e.g. a dropped
#    appendix) don't linger as stale orphan files in local builds.
rm -rf output/web
"$PRETEXT" build web

# 3. Quick-lookup search index (entries.json is gitignored, so regenerate it).
"$PYTHON" workflow/scripts/build-search-index.py

# 4. Bundle the quick-lookup page; stop Jekyll from dropping PreTeXt's _static/.
cp assets/search/tra-cuu.html assets/search/lookup.js assets/search/entries.json output/web/
touch output/web/.nojekyll

# 5. Bundle FontAwesome locally (no CDN) for the acknowledgement channel icons.
cp -r assets/fontawesome output/web/fontawesome

# 6. Rewrite acknowledgement channel-icon tokens into FontAwesome glyphs.
"$PYTHON" workflow/scripts/postprocess-web.py output/web

echo "Built output/web (acknowledgements + search index + channel icons)"
