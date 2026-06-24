#!/usr/bin/env python3
"""Patch the PreTeXt-generated main.tex to embed the designed cover as page 1
and drop PreTeXt's half-title + title page.

Embedding the cover *inside* the LaTeX compile (via pdfpages) keeps the book a
single document, so cross-reference hyperlinks and their named destinations
survive — unlike merging a separate cover PDF afterwards (pdfunite / qpdf /
ghostscript all strip the body's named destinations on merge).

Usage: patch-cover-tex.py output/latex/main.tex
"""
import re, sys

f = sys.argv[1]
s = open(f, encoding="utf-8").read()

# 1. Load pdfpages at the end of the preamble.
if "\\usepackage{pdfpages}" not in s:
    s = s.replace("\\begin{document}", "\\usepackage{pdfpages}\n\\begin{document}", 1)

# 2. Replace the half-title block with the embedded cover (page 1).
s, n1 = re.subn(
    r"%% begin: half-title.*?%% end:   half-title\n",
    "%% cover (embedded so cross-reference links survive)\n"
    "\\\\includepdf[pages=1,fitpaper=true]{external/cover-front.pdf}\n",
    s, count=1, flags=re.S)

# 3. Drop PreTeXt's title page (the cover already carries the title/author).
s, n2 = re.subn(r"%% begin: title page.*?%% end:   title page\n", "", s, count=1, flags=re.S)

open(f, "w", encoding="utf-8").write(s)
print(f"patched {f}: pdfpages + cover includepdf ({n1}), dropped title page ({n2})")
if not (n1 and n2):
    sys.exit("WARNING: expected title-page markers not found — cover/title patch incomplete")
