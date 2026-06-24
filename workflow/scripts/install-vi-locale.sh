#!/usr/bin/env bash
# Install the repo's Vietnamese localization into the active PreTeXt install
# (PreTeXt 2.42 ships no vi locale). Idempotent — safe to run before every build
# (local and CI). Copies assets/localizations/vi-VN.xml into PreTeXt's
# localizations directory and registers it in localizations.xml.
set -e
cd "$(dirname "$0")/../.."
SRC=assets/localizations/vi-VN.xml
find_loc() { find "$HOME/.ptx" -type d -path '*xsl/localizations' 2>/dev/null | sort -r | head -1; }
LOC=$(find_loc)

# PreTeXt downloads its core resources (where the localizations dir lives) to
# ~/.ptx on the first build. On a fresh machine (e.g. CI) the dir is absent
# until then, so trigger a throwaway build to fetch them, then look again.
if [ -z "$LOC" ] && command -v pretext >/dev/null 2>&1; then
  echo "PreTeXt core not present yet; fetching resources via a throwaway build…" >&2
  pretext build web >/dev/null 2>&1 || true
  LOC=$(find_loc)
fi
if [ -z "$LOC" ]; then
  echo "WARNING: PreTeXt localizations directory not found; Vietnamese labels unavailable." >&2
  exit 0
fi
cp "$SRC" "$LOC/vi-VN.xml"
if ! grep -q 'vi-VN' "$LOC/localizations.xml"; then
  python3 - "$LOC/localizations.xml" <<'PY'
import sys
f = sys.argv[1]; s = open(f, encoding="utf-8").read()
s = s.replace("</localizations>",
              "    <locale>vi-VN</locale><filename>vi-VN.xml</filename>\n</localizations>", 1)
open(f, "w", encoding="utf-8").write(s)
PY
fi
echo "Installed vi-VN locale into $LOC"
