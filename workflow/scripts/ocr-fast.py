#!/usr/bin/env python3
"""Fast OCR of a scanned PDF into workflow/corpus/<biblio_id>.txt.

Same @@PAGE n@@ output format as ocr-pdf.py, but tuned for throughput on this
host: tessdata_fast models + OMP_THREAD_LIMIT=1 (one thread per tesseract so N
pages run in parallel without OpenMP thrashing). ~2s/page @200dpi vs ~100s/page
with the heavy tessdata_best model + default multithreading.

Usage: ocr-fast.py <biblio_id> --pdf /path/file.pdf [--dpi 200] [--psm 3]
"""
import argparse, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "corpus")
FAST = os.path.expanduser("~/.local/share/tessdata_fast")

def pages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    for ln in out.splitlines():
        if ln.startswith("Pages:"):
            return int(ln.split()[1])
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("biblio_id")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--psm", default="3")
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--last", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if not os.path.exists(a.pdf):
        sys.exit(f"PDF not found: {a.pdf}")
    env = dict(os.environ, TESSDATA_PREFIX=FAST, OMP_THREAD_LIMIT="1")
    n = pages(a.pdf)
    last = a.last or n
    os.makedirs(CORPUS, exist_ok=True)
    dst = a.out or os.path.join(CORPUS, a.biblio_id + ".txt")
    print(f"OCR-fast {os.path.basename(a.pdf)} -> {os.path.basename(dst)} | pages {a.first}-{last}/{n} @{a.dpi}dpi psm{a.psm}", flush=True)
    with tempfile.TemporaryDirectory() as td, open(dst, "w", encoding="utf-8") as out:
        for p in range(a.first, last + 1):
            base = os.path.join(td, "pg")
            subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(a.dpi),
                            "-gray", "-png", "-singlefile", a.pdf, base],
                           check=True, capture_output=True)
            r = subprocess.run(["tesseract", base + ".png", "stdout", "-l", "vie+eng",
                                "--psm", a.psm], capture_output=True, text=True, env=env)
            out.write(f"@@PAGE {p}@@\n{r.stdout}\n")
            if p % 25 == 0:
                print(f"  {a.biblio_id}: {p}/{n}", flush=True)
    mpath = os.path.join(CORPUS, "manifest.json")
    man = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else {}
    man[a.biblio_id] = {"origin": "ocr-fast", "engine": "tesseract:vie+eng(fast)",
                        "dpi": a.dpi, "psm": a.psm, "pages": f"1-{n}", "complete": True}
    json.dump(man, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  {a.biblio_id}: DONE {n} pages", flush=True)

if __name__ == "__main__":
    main()
