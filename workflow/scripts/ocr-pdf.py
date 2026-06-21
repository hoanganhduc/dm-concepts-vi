#!/usr/bin/env python3
"""OCR a scanned (image-only) PDF into the local text corpus.

This is the FALLBACK path for sources with no text layer (see triage in
docs/PLAN.md). It rasterizes each page and runs OCR, writing
workflow/corpus/<biblio_id>.txt in the same "@@PAGE n@@" format that find-term.py
reads, so OCR'd books mine identically to born-digital ones.

OCR engine chain (first available wins):
  1. tesseract  -l vie+eng   (Vietnamese model in ~/.local/share/tessdata)
  2. rapidocr_onnxruntime     (lightweight, multilingual)  -- if installed
  3. easyocr     Reader(['vi','en'])                        -- if installed
If none can handle Vietnamese, it exits with guidance instead of producing
garbage.

A manifest (workflow/corpus/manifest.json) records origin=ocr so miners/verifiers
know these citations are OCR-derived (use find-term.py --loose to tolerate
diacritic noise).

Usage:
  ocr-pdf.py bib-leanhvinh-2020                 # whole book
  ocr-pdf.py bib-leanhvinh-2020 --first 20 --last 40
  ocr-pdf.py bib-x --pdf "/path/to/file.pdf" --dpi 300
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "workflow", "corpus")
STAGING = "/home/ubuntu/.openclaw/workspace/data/research/zotero/staging"
TESSDATA = os.path.expanduser("~/.local/share/tessdata")

# Known scanned sources -> staging filename (override with --pdf).
STAGED = {
    "bib-rosen-2003-vi": "Rosen_2003_Toán rời rạc ứng dụng trong tin học [Book].pdf",
    "bib-leanhvinh-2020": "Lê_2020_Lý thuyết đồ thị [Book].pdf",
    "bib-hoangchithanh-2007": "Hoàng_2007_Đồ thị và các thuật toán [Book].pdf",
    "bib-hoangchithanh-2011": "Hoàng_2011_Lý thuyết đồ thị - Lý thuyết-Bài tập-Trắc nghiệm [Book].pdf",
}


def have_tesseract_vie():
    if not shutil.which("tesseract"):
        return False
    env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)
    out = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True, env=env)
    return "vie" in (out.stdout + out.stderr)


def make_ocr_engine():
    """Return (name, fn(png_path)->text) for the first available VI-capable engine."""
    if have_tesseract_vie():
        env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)

        def run(png):
            r = subprocess.run(["tesseract", png, "stdout", "-l", "vie+eng", "--psm", "3"],
                               capture_output=True, text=True, env=env)
            return r.stdout
        return "tesseract:vie+eng", run

    try:
        from rapidocr_onnxruntime import RapidOCR  # noqa
        engine = RapidOCR()

        def run(png):
            res, _ = engine(png)
            return "\n".join(line[1] for line in (res or []))
        return "rapidocr", run
    except Exception:
        pass

    try:
        import easyocr  # noqa
        reader = easyocr.Reader(["vi", "en"], gpu=False)

        def run(png):
            return "\n".join(reader.readtext(png, detail=0, paragraph=True))
        return "easyocr:vi", run
    except Exception:
        pass

    sys.exit("No Vietnamese-capable OCR engine available. Install the tesseract "
             "'vie' model into ~/.local/share/tessdata, or `pip install "
             "rapidocr_onnxruntime` (lightweight) / `pip install easyocr`.")


def page_count(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("biblio_id")
    ap.add_argument("--pdf", default=None)
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--last", type=int, default=0)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    pdf = args.pdf or os.path.join(STAGING, STAGED.get(args.biblio_id, ""))
    if not os.path.exists(pdf):
        sys.exit(f"PDF not found for {args.biblio_id}: {pdf} (use --pdf)")

    name, ocr = make_ocr_engine()
    total = page_count(pdf)
    last = args.last or total
    os.makedirs(CORPUS, exist_ok=True)
    dst = os.path.join(CORPUS, args.biblio_id + ".txt")
    full = args.first == 1 and last >= total

    print(f"OCR engine: {name} | {os.path.basename(pdf)} | pages {args.first}-{last}/{total} @ {args.dpi}dpi")
    mode = "w" if full else "a"
    with tempfile.TemporaryDirectory() as td, open(dst, mode, encoding="utf-8") as out:
        for p in range(args.first, last + 1):
            base = os.path.join(td, "pg")
            subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(args.dpi),
                            "-gray", "-png", "-singlefile", pdf, base],
                           check=True, capture_output=True)
            text = ocr(base + ".png")
            out.write(f"@@PAGE {p}@@\n{text}\n")
            if p % 10 == 0 or p == last:
                print(f"  ...page {p}")

    # manifest: mark this source as OCR-derived
    mpath = os.path.join(CORPUS, "manifest.json")
    man = {}
    if os.path.exists(mpath):
        man = json.load(open(mpath, encoding="utf-8"))
    man[args.biblio_id] = {"origin": "ocr", "engine": name, "dpi": args.dpi,
                           "pages": f"{args.first}-{last}", "complete": full}
    json.dump(man, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Wrote {os.path.relpath(dst, ROOT)} ({'full' if full else 'partial'}); manifest updated.")


if __name__ == "__main__":
    main()
