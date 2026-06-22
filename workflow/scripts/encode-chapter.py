#!/usr/bin/env python3
"""Encode a panel-approved chapter (workflow/panels/chapter-<L>-final.json) into
both the data file (data/terms/entries-<l>.yaml) and the PreTeXt source
(source/ch-<l>.ptx).

- vi_terms are grouped by Vietnamese term (one display line per distinct term,
  with all its source+page citations).
- Math written as $$...$$ in the data is converted to <m>...</m> in PreTeXt.
- see_also <xref> is emitted only for ids present in THIS chapter; cross-chapter
  forward references are preserved in the YAML but not linked yet.

Usage: encode-chapter.py c
"""
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def esc_text(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # LaTeX / markdown emphasis habits from drafters -> PreTeXt <em>
    s = re.sub(r"\\(?:emph|textit|textbf)\{([^{}]*)\}", r"<em>\1</em>", s)
    s = re.sub(r"\*([^*\n]{1,80}?)\*", r"<em>\1</em>", s)
    return s


def esc_math(s):
    # PreTeXt math source: <, >, & must be the XML-safe macros \lt, \gt, \amp.
    return s.replace("&", " \\amp ").replace("<", " \\lt ").replace(">", " \\gt ")


def to_ptx(text):
    """Convert prose with $$...$$ inline math and ```math fenced blocks into
    PreTeXt mixed content (<m> inline, <me> display)."""
    text = text or ""
    token = re.compile(r"```math\s*(.+?)```|\$\$(.+?)\$\$", re.S)
    out, last = [], 0
    for m in token.finditer(text):
        out.append(esc_text(text[last:m.start()]))
        if m.group(1) is not None:
            out.append("<me>" + esc_math(m.group(1).strip()) + "</me>")
        else:
            out.append("<m>" + esc_math(m.group(2).strip()) + "</m>")
        last = m.end()
    out.append(esc_text(text[last:]))
    return "".join(out)


def group_terms(vi_terms):
    """Group vi_terms by term text, preserving recommended flag and citations."""
    groups = []
    index = {}
    for t in vi_terms:
        key = t.get("term", "")
        if key not in index:
            index[key] = {"term": key, "recommended": False, "cites": []}
            groups.append(index[key])
        g = index[key]
        g["recommended"] = g["recommended"] or bool(t.get("recommended"))
        if t.get("verified") and t.get("source_id") and str(t.get("page", "")).strip():
            g["cites"].append((t["source_id"], str(t["page"]).strip()))
    # recommended term first
    groups.sort(key=lambda g: (not g["recommended"], g["term"]))
    return groups


def render_see(e, allowed_ids):
    """Render a cross-reference stub: 'Headword (vi). Xem <target>.'"""
    eid = e["id"]
    target = e["see_ref"]
    lines = [f'  <definition xml:id="def-{eid}">',
             f"    <title>{esc_text(e['headword_en'])}</title>",
             f"    <idx><h>{esc_text(e['headword_en'].lower())}</h></idx>"]
    vi_terms = sorted({t.get("term", "") for t in e.get("vi_terms", []) if t.get("term")})
    for term in vi_terms:
        lines.append(f"    <idx><h>{esc_text(term)}</h></idx>")
    see = (f'<xref ref="def-{target}" text="title" />' if target in allowed_ids
           else f"<em>{esc_text(target)}</em>")
    vi = ", ".join(vi_terms)
    body = f"<term>{esc_text(e['headword_en'])}</term>"
    if vi:
        body += f" ({esc_text(vi)})"
    body += f". Xem {see}."
    lines.append(f"    <statement><p>{body}</p></statement>")
    lines.append("  </definition>")
    return "\n".join(lines)


def render_entry(e, allowed_ids):
    eid = e["id"]
    if e.get("see_ref"):
        return render_see(e, allowed_ids)
    rec = next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), "")
    lines = []
    lines.append(f'  <definition xml:id="def-{eid}">')
    title = esc_text(e["headword_en"]) + (" — " + esc_text(rec) if rec else "")
    lines.append(f"    <title>{title}</title>")
    seen = set()
    for h in [e["headword_en"].lower()] + sorted({t.get("term", "") for t in e.get("vi_terms", []) if t.get("term")}):
        if h and h.lower() not in seen:
            seen.add(h.lower())
            lines.append(f"    <idx><h>{esc_text(h)}</h></idx>")
    nota = (e.get("notation") or "").replace("$$", "").strip()
    if nota:
        lines.append("    <notation>")
        lines.append(f"      <usage><m>{esc_math(nota)}</m></usage>")
        lines.append(f"      <description>{esc_text(rec or e['headword_en'])}</description>")
        lines.append("    </notation>")
    lines.append("    <statement>")
    raw = (e.get("definition_vi", "") or "").rstrip()
    if e.get("rosen_ref") and raw.endswith("."):
        raw = raw[:-1].rstrip()
    defn = to_ptx(raw)
    if e.get("rosen_ref"):
        defn += f' (theo <xref ref="bib-rosen-2019" />, {esc_text(e["rosen_ref"])}).'
    lines.append(f"      <p>{defn}</p>")
    lines.append("      <p>Thuật ngữ tiếng Việt tương ứng:</p>")
    lines.append("      <ul>")
    for g in group_terms(e.get("vi_terms", [])):
        body = f"<term>{esc_text(g['term'])}</term>"
        if g["cites"]:
            cites = "; ".join(f'<xref ref="{sid}" /> ({esc_text(pg)})' for sid, pg in g["cites"])
            body += " " + cites
        else:
            note = ("thuật ngữ chuẩn; chưa truy được trong kho văn bản"
                    if g["recommended"] else "biến thể, chưa có trích dẫn cụ thể")
            body += f" <em>({note})</em>"
        if g["recommended"]:
            body += " — cách dùng phổ biến"
        lines.append(f"        <li><p>{body}.</p></li>")
    lines.append("      </ul>")
    if e.get("example_vi"):
        lines.append(f"      <p>Ví dụ: {to_ptx(e['example_vi'])}</p>")
    seealso = [s for s in (e.get("see_also") or []) if s in allowed_ids and s != eid]
    if seealso:
        xrefs = ", ".join(f'<xref ref="def-{s}" text="title" />' for s in seealso)
        lines.append(f"      <p>Xem thêm {xrefs}.</p>")
    lines.append("    </statement>")
    lines.append("  </definition>")
    return "\n".join(lines)


def update_main_includes():
    """Rewrite the auto-managed chapter <xi:include> block in source/main.ptx
    from the set of existing source/ch-*.ptx files, in alphabetical letter order."""
    import glob as _glob
    main_path = os.path.join(ROOT, "source", "main.ptx")
    text = open(main_path, encoding="utf-8").read()
    chs = [os.path.basename(p)[:-4] for p in _glob.glob(os.path.join(ROOT, "source", "ch-*.ptx"))]
    chs = sorted(chs, key=lambda c: c.split("-", 1)[1])
    block = "\n".join('    <xi:include href="./%s.ptx" />' % c for c in chs)
    new = re.sub(
        r"(<!-- BEGIN chapter includes \(auto-managed\) -->\n).*?(\n[ \t]*<!-- END chapter includes -->)",
        lambda m: m.group(1) + block + m.group(2), text, flags=re.S)
    open(main_path, "w", encoding="utf-8").write(new)
    return chs


def global_entry_ids():
    """All entry ids already encoded into data/terms/entries-*.yaml (post-guard),
    so see_also can link across chapters once every chapter exists."""
    import glob as _glob
    ids = set()
    for f in _glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml")):
        doc = yaml.safe_load(open(f, encoding="utf-8")) or {}
        for e in doc.get("entries", []):
            if e.get("id"):
                ids.add(e["id"])
    return ids


def main():
    letter = (sys.argv[1] if len(sys.argv) > 1 else "c").lower()
    src = os.path.join(ROOT, "workflow", "panels", f"chapter-{letter}-final.json")
    data = json.load(open(src, encoding="utf-8"))
    L = letter.upper()
    # Guard: drop any entry whose headword does not start with this chapter's
    # letter (the term extractor occasionally misfiles a term).
    all_entries = data["final_entries"]
    entries = [e for e in all_entries if e.get("headword_en", "")[:1].upper() == L]
    dropped = [e.get("id") for e in all_entries if e.get("headword_en", "")[:1].upper() != L]
    if dropped:
        print(f"WARN dropped wrong-initial entries (not '{L}'): {dropped}")
    allowed_ids = global_entry_ids() | {e["id"] for e in entries}

    # ---- data/terms/entries-<l>.yaml ----
    ydoc = {"letter": L, "entries": []}
    for e in entries:
        ydoc["entries"].append({
            "id": e["id"], "letter": L, "headword_en": e["headword_en"],
            "notation": e.get("notation", ""), "rosen_ref": e.get("rosen_ref", ""),
            "definition_vi": e.get("definition_vi", ""), "example_vi": e.get("example_vi", ""),
            "vi_terms": [{
                "term": t.get("term", ""), "source_id": t.get("source_id", ""),
                "page": t.get("page", ""), "recommended": bool(t.get("recommended")),
                "verified": bool(t.get("verified")), "pdf_page": t.get("pdf_page"),
                "snippet": t.get("snippet", ""),
            } for t in e.get("vi_terms", [])],
            "see_also": e.get("see_also", []), "status": e.get("status", "panel-approved"),
            "see_ref": e.get("see_ref", ""), "notes": e.get("notes", ""),
        })
    ypath = os.path.join(ROOT, "data", "terms", f"entries-{letter}.yaml")
    with open(ypath, "w", encoding="utf-8") as fh:
        fh.write("# Chapter %s entries — panel-approved (Phase 1). Source of truth.\n" % L)
        fh.write("# Generated by encode-chapter.py from workflow/panels/chapter-%s-final.json\n" % letter)
        yaml.safe_dump(ydoc, fh, allow_unicode=True, sort_keys=False, width=100)

    # ---- source/ch-<l>.ptx ----
    body = [render_entry(e, allowed_ids) for e in entries]
    ptx = f'''<?xml version="1.0" encoding="UTF-8"?>
<chapter xml:id="ch-{letter}" xmlns:xi="http://www.w3.org/2001/XInclude">
  <title>{L}</title>

  <introduction>
    <p>
      Chương này tập hợp các thuật ngữ tiếng Anh bắt đầu bằng chữ <q>{L}</q>, kèm
      định nghĩa và các thuật ngữ tiếng Việt tương ứng cùng trích dẫn nguồn.
    </p>
  </introduction>

{chr(10).join(body)}
</chapter>
'''
    ppath = os.path.join(ROOT, "source", f"ch-{letter}.ptx")
    open(ppath, "w", encoding="utf-8").write(ptx)
    chs = update_main_includes()
    print(f"Wrote {len(entries)} entries -> {os.path.relpath(ypath, ROOT)} and {os.path.relpath(ppath, ROOT)}")
    print(f"main.ptx chapters: {', '.join(chs)}")


if __name__ == "__main__":
    main()
