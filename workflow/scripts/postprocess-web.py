#!/usr/bin/env python3
"""Post-process the built HTML (output/web) for acknowledgement channel icons.

gen-acknowledgements.py emits portable tokens (@@person@@ / @@github@@). Here we
rewrite them to FontAwesome <i> glyphs and add the FontAwesome stylesheet to the
<head> of any page that uses them (only the acknowledgements page in practice).
Idempotent: safe to run more than once.

Usage: postprocess-web.py [output/web]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FA_LINK = (
    '<link rel="stylesheet" '
    'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" '
    'crossorigin="anonymous" referrerpolicy="no-referrer">'
)
TOKENS = {
    "@@person@@": '<i class="fa-solid fa-user" aria-hidden="true"></i>',
    "@@github@@": '<i class="fa-brands fa-github" aria-hidden="true"></i>',
}


def process(html: str) -> str:
    if not any(tok in html for tok in TOKENS):
        return html
    for tok, glyph in TOKENS.items():
        html = html.replace(tok, glyph)
    if "font-awesome" not in html and "</head>" in html:
        html = html.replace("</head>", f"  {FA_LINK}\n</head>", 1)
    return html


def strip_tokens(text: str) -> str:
    """Remove the bare tokens (no icon) — for the full-text search index, whose
    snippets should show just the contributor name."""
    for tok in TOKENS:
        text = text.replace(tok + " ", "").replace(tok, "")
    return text


def main() -> int:
    web = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output" / "web"
    if not web.is_dir():
        sys.exit(f"web output not found: {web}")
    changed = 0
    for path in web.glob("*.html"):
        original = path.read_text(encoding="utf-8")
        updated = process(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    # PreTeXt's lunr full-text index embeds page text verbatim — clean the
    # tokens out of it so search snippets don't show "@@person@@".
    for idx in web.glob("*search-index*.js"):
        original = idx.read_text(encoding="utf-8")
        updated = strip_tokens(original)
        if updated != original:
            idx.write_text(updated, encoding="utf-8")
    print(f"postprocess-web: added channel icons to {changed} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
