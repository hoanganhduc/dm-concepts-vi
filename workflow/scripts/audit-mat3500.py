#!/usr/bin/env python3
"""Audit the MAT3500 course terminology against the book.

Extracts English<->Vietnamese term pairs from the course lectures (the
\\EMPH{vi (en)} / \\emph / \\textbf pattern) and cross-checks each against the
book entries:

  - MISSING            : course EN term has no book headword (coverage gap)
  - CONSISTENT         : book recommended VI == course VI (good)
  - VARIANT            : course VI is a listed book variant, but the book
                         recommends a different lead term (review)
  - VI_DIFFERS         : course VI absent from the book's variants (mismatch)

Writes a full report to docs/mat3500-audit.md and prints a summary.
"""
import glob
import os
import re
import unicodedata

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LECTURES = os.path.expanduser("~/VNU-HUS-MAT3500/Lectures")
EMPH = re.compile(r"\\(?:EMPH|emph|textbf|textit)\{([^{}]*?)\(([^()]*?)\)[^{}]*?\}")
EN_OK = re.compile(r"[a-z][a-z0-9 \-'/]*")


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "d").lower().strip()


def course_terms():
    pairs = {}
    for t in glob.glob(os.path.join(LECTURES, "**", "*.tex"), recursive=True):
        try:
            s = open(t, encoding="utf-8").read()
        except Exception:
            continue
        topic = os.path.basename(os.path.dirname(t))
        for m in EMPH.finditer(s):
            vi = m.group(1).strip(" ,.")
            en = m.group(2).strip().lower()
            if not EN_OK.fullmatch(en) or len(en) < 2 or not vi:
                continue
            d = pairs.setdefault(en, {"en": en, "vi": set(), "topics": set()})
            d["vi"].add(vi)
            d["topics"].add(topic)
    return pairs


def book_index():
    idx = {}
    for f in glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml")):
        doc = yaml.safe_load(open(f, encoding="utf-8")) or {}
        for e in doc.get("entries", []):
            hw = (e.get("headword_en") or "").lower().strip()
            rec = next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), "")
            variants = [t.get("term", "") for t in e.get("vi_terms", [])]
            idx[hw] = {"id": e["id"], "rec": rec, "variants": variants}
    return idx


def match_book(en, idx):
    if en in idx:
        return idx[en]
    if en + "s" in idx:
        return idx[en + "s"]
    if en.endswith("s") and en[:-1] in idx:
        return idx[en[:-1]]
    return None


def main():
    course = course_terms()
    book = book_index()
    cats = {"MISSING": [], "CONSISTENT": [], "VARIANT": [], "VI_DIFFERS": []}
    for en, d in sorted(course.items()):
        b = match_book(en, book)
        course_vi = sorted(d["vi"])
        if not b:
            cats["MISSING"].append((en, course_vi, sorted(d["topics"])))
            continue
        rec_n = norm(b["rec"])
        var_n = {norm(v) for v in b["variants"]}
        cvi_n = {norm(v) for v in course_vi}
        if cvi_n & {rec_n}:
            cats["CONSISTENT"].append((en, b["rec"], course_vi))
        elif cvi_n & var_n:
            cats["VARIANT"].append((en, b["rec"], course_vi))
        else:
            cats["VI_DIFFERS"].append((en, b["rec"], course_vi))

    lines = ["# Đối chiếu thuật ngữ MAT3500 ↔ sách\n",
             f"Tổng thuật ngữ EN↔VI rút từ bài giảng: **{len(course)}**.\n",
             "| Hạng mục | Số lượng |", "|---|---|",
             f"| ✅ Khớp bản dịch (CONSISTENT) | {len(cats['CONSISTENT'])} |",
             f"| ⚠️ Sách khuyến nghị khác (VARIANT) | {len(cats['VARIANT'])} |",
             f"| ❗ Bản dịch khác hẳn (VI_DIFFERS) | {len(cats['VI_DIFFERS'])} |",
             f"| ❌ Thiếu trong sách (MISSING) | {len(cats['MISSING'])} |", ""]

    lines.append("## ❗ Bản dịch khác (sách nên xem lại / bổ sung biến thể)\n")
    for en, rec, cvi in cats["VI_DIFFERS"]:
        lines.append(f"- **{en}** — sách: `{rec}` · bài giảng: {', '.join(cvi)}")
    lines.append("\n## ⚠️ Sách khuyến nghị thuật ngữ khác với bài giảng\n")
    for en, rec, cvi in cats["VARIANT"]:
        lines.append(f"- **{en}** — sách khuyến nghị: `{rec}` · bài giảng dùng: {', '.join(cvi)}")
    lines.append("\n## ❌ Thuật ngữ bài giảng chưa có trong sách\n")
    for en, cvi, topics in cats["MISSING"]:
        lines.append(f"- **{en}** — bài giảng: {', '.join(cvi)}  _(ở: {', '.join(topics)})_")

    dest = os.path.join(ROOT, "docs", "mat3500-audit.md")
    open(dest, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"course terms: {len(course)}")
    for k in ("CONSISTENT", "VARIANT", "VI_DIFFERS", "MISSING"):
        print(f"  {k}: {len(cats[k])}")
    print(f"report -> {os.path.relpath(dest, ROOT)}")


if __name__ == "__main__":
    main()
