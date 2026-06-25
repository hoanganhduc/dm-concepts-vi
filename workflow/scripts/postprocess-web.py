#!/usr/bin/env python3
"""Post-process the built HTML (output/web).

  1. Acknowledgement channel icons: rewrite the portable tokens emitted by
     gen-acknowledgements.py (@@person@@ / @@github@@) to FontAwesome <i> glyphs
     and add the (locally bundled) FontAwesome stylesheet where used; also strip
     the tokens from the lunr full-text index.
  2. Cover card on the title page (frontmatter.html): the designed cover image
     plus a "Tải bản PDF" button (the print cover is not shown on the web by
     default).
  3. Page footer (every page): a Release line linking to the GitHub releases
     page, and the Creative Commons BY-NC-SA badge.

Idempotent: safe to run more than once. Run by build-web.sh after `pretext
build web`. assets/cover-front.png and assets/cc-by-nc-sa.png are copied into
output/web by build-web.sh.

Usage: postprocess-web.py [output/web]
"""
from __future__ import annotations

import datetime
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FA_CSS_HREF = "fontawesome/css/all.min.css"
FA_LINK = f'<link rel="stylesheet" href="{FA_CSS_HREF}">'
TOKENS = {
    "@@person@@": '<i class="fa-solid fa-user" aria-hidden="true"></i>',
    "@@github@@": '<i class="fa-brands fa-github" aria-hidden="true"></i>',
}

REPO = "https://github.com/hoanganhduc/dm-concepts-vi"
RELEASES = f"{REPO}/releases/latest"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
# Release tag in CI (RELEASE_VERSION) or the build date for a plain web build.
VERSION = os.environ.get("RELEASE_VERSION") or datetime.date.today().strftime("%Y.%m.%d")

# The theme hides #ptx-page-footer, so inject at the end of the visible main
# content (just before </main>) instead, styled as a footer bar.
FOOTER_ANCHOR = "</main>"
FOOTER_BLOCK = (
    '<div class="dm-web-footer" style="display:flex;align-items:center;'
    'justify-content:center;gap:1.2rem;flex-wrap:wrap;font-size:.9rem;'
    'max-width:840px;margin:2.5rem auto 1rem;padding-top:1rem;'
    'border-top:1px solid #d0d7de;">'
    f'<a href="{RELEASES}" style="font-family:monospace;color:#2C7A7B;'
    f'text-decoration:none;">Release {VERSION}</a>'
    f'<a href="{LICENSE_URL}" title="CC BY-NC-SA 4.0">'
    '<img src="cc-by-nc-sa.png" alt="CC BY-NC-SA 4.0" '
    'style="height:28px;vertical-align:middle;"></a>'
    '</div>'
)

COVER_ANCHOR = '<section class="frontmatter" id="frontmatter">'
COVER_CARD = (
    '<div class="dm-cover-card" style="text-align:center;margin:1rem 0 2rem;">'
    f'<a href="{RELEASES}" title="Tải bản PDF mới nhất">'
    '<img src="cover-front.png" alt="Bìa sách" '
    'style="max-width:280px;width:100%;height:auto;'
    'box-shadow:0 3px 12px rgba(0,0,0,.25);border-radius:4px;"></a>'
    '<div style="margin-top:1rem;">'
    f'<a href="{RELEASES}" style="display:inline-block;padding:.7rem 1.4rem;'
    'background:#0F2A43;color:#fff;border-radius:6px;text-decoration:none;'
    'font-weight:600;font-size:1.05rem;">⬇ Tải bản PDF</a></div></div>'
)


def process(path: Path, html: str) -> str:
    # 1. channel icons
    if any(tok in html for tok in TOKENS):
        for tok, glyph in TOKENS.items():
            html = html.replace(tok, glyph)
        if FA_CSS_HREF not in html and "</head>" in html:
            html = html.replace("</head>", f"  {FA_LINK}\n</head>", 1)
    # 2. cover card on the title page only
    if path.name == "frontmatter.html" and "dm-cover-card" not in html and COVER_ANCHOR in html:
        html = html.replace(COVER_ANCHOR, COVER_ANCHOR + COVER_CARD, 1)
    # 3. footer (every page): before </main> so it stays visible
    if "dm-web-footer" not in html and FOOTER_ANCHOR in html:
        html = html.replace(FOOTER_ANCHOR, FOOTER_BLOCK + FOOTER_ANCHOR, 1)
    return html


def strip_tokens(text: str) -> str:
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
        updated = process(path, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    for idx in web.glob("*search-index*.js"):
        original = idx.read_text(encoding="utf-8")
        updated = strip_tokens(original)
        if updated != original:
            idx.write_text(updated, encoding="utf-8")
    print(f"postprocess-web: footer + cover card + icons on {changed} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
