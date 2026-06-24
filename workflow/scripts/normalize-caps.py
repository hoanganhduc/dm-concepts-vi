#!/usr/bin/env python3
"""Normalise headword / Vietnamese-term capitalisation across all panels.

Convention (chosen by the editor): English headwords are lowercase, keeping only
proper nouns (Boole, Euler, ...), acronyms (NP, RSA, XOR, ...) and single-letter
math symbols (P, Z, K_n). Vietnamese terms are lowercase too, keeping the same
proper nouns/acronyms (Vietnamese does not capitalise common nouns).

Source of truth is workflow/panels/chapter-<l>-final.json (fields headword_en and
vi_terms[].term). Dry-run by default; pass --apply to write the JSON back, then
re-run encode-chapter.py to regenerate the .ptx / .yaml.
"""
import json, glob, re, sys

# Proper nouns: lowercase form -> canonical form. Possessives ('s) handled by
# stripping the suffix before lookup, so list only the base name.
NAMES = {
    "boolean": "Boolean", "boole": "Boole",
    "euler": "Euler", "eulerian": "Eulerian", "euclidean": "Euclidean",
    "euclid": "Euclid", "euclid's": "Euclid's",
    "hamilton": "Hamilton", "hamiltonian": "Hamiltonian",
    "cartesian": "Cartesian", "cantor": "Cantor", "bernoulli": "Bernoulli",
    "carmichael": "Carmichael", "dijkstra": "Dijkstra",
    "eratosthenes": "Eratosthenes", "fibonacci": "Fibonacci", "fermat": "Fermat",
    "gray": "Gray", "hasse": "Hasse", "huffman": "Huffman", "jordan": "Jordan",
    "johnson": "Johnson", "jacobi": "Jacobi", "kruskal": "Kruskal",
    "karnaugh": "Karnaugh", "kuratowski": "Kuratowski", "latin": "Latin",
    "mersenne": "Mersenne", "turing": "Turing", "pascal": "Pascal",
    "petersen": "Petersen", "polish": "Polish", "quine": "Quine",
    "mccluskey": "McCluskey", "ramsey": "Ramsey", "stirling": "Stirling",
    "dirichlet": "Dirichlet", "venn": "Venn", "vandermonde": "Vandermonde",
    "warshall": "Warshall", "young": "Young", "zorn": "Zorn",
    "chinese": "Chinese", "konigsberg": "Königsberg", "königsberg": "Königsberg",
    "de": "De", "morgan": "Morgan",
    # names that appear mainly on the Vietnamese side
    "descartes": "Descartes", "prim": "Prim", "bayes": "Bayes",
    "catalan": "Catalan", "lucas": "Lucas", "newton": "Newton",
    "godel": "Gödel", "gödel": "Gödel", "abel": "Abel", "abelian": "Abelian",
    "caesar": "Caesar", "gale": "Gale", "shapley": "Shapley", "veitch": "Veitch",
    "ven": "Ven", "euclide": "Euclide", "pontragin": "Pontragin", "bool": "Bool",
    "ơle": "Ơle", "hamintơn": "Hamintơn", "nêpe": "Nêpe", "ômêga": "Ômêga",
}

# Vietnamese terms keep proper nouns and acronyms; only the (sentence-case) first
# letter is lowered. A few common words were left upper mid-term by Title-casing.
VI_PHRASE_FIXES = [("Quy nạp", "quy nạp"), ("Thứ nhất", "thứ nhất"),
                   ("Bốn màu", "bốn màu")]


def normalize_vi(term):
    """Lowercase only the first letter (unless the first word is a proper noun or
    acronym), then fix the few mid-term Title-cased common words."""
    m = WORD.search(term)
    if m:
        first = m.group(0)
        if not (first.lower() in NAMES or (len(first) >= 2 and first.isupper())):
            i = m.start()
            if term[i].isupper():
                term = term[:i] + term[i].lower() + term[i + 1:]
    for a, b in VI_PHRASE_FIXES:
        term = term.replace(a, b)
    return term

# Exact original headword -> final form, for the few single-letter cases where
# the Title-Case wrongly upper-cased a variable (r, m) that should stay lower.
OVERRIDES = {
    "R-Combination": "r-combination",
    "R-Permutation": "r-permutation",
    "Inverse Modulo M": "inverse modulo m",
}

# Logic-gate phrases: the operator is an acronym only in "<op> gate".
GATE_FIXES = [(re.compile(rf"\b{op}\s+gate\b", re.I), f"{op.upper()} gate")
              for op in ("and", "or", "not", "nand", "nor", "xor", "xnor")]

WORD = re.compile(r"[A-Za-zÀ-ỹ][A-Za-zÀ-ỹ'’]*")


def fix_word(tok):
    """Lowercase one token, but keep acronyms, proper nouns and single letters."""
    if len(tok) >= 2 and tok.isupper():          # acronym already upper: NP, XOR, RSA
        return tok
    base, suff = (tok[:-2], tok[-2:]) if tok.lower().endswith("'s") else (tok, "")
    canon = NAMES.get(base.lower())
    if canon:
        return canon + suff
    if len(tok) == 1:                            # single-letter symbol: P, Z, K, n
        return tok.lower() if tok in ("A", "I") else tok   # but not the article a / I
    return tok.lower()


def normalize(text):
    if text in OVERRIDES:
        return OVERRIDES[text]
    out = WORD.sub(lambda m: fix_word(m.group(0)), text)
    for rx, repl in GATE_FIXES:
        out = rx.sub(repl, out)
    return out


def main():
    apply = "--apply" in sys.argv
    en_changes, vi_changes, kept_caps, math_terms = [], [], [], []
    for f in sorted(glob.glob("workflow/panels/chapter-*-final.json")):
        d = json.load(open(f, encoding="utf-8"))
        dirty = False
        for e in d.get("final_entries", []):
            h = e.get("headword_en", "")
            nh = normalize(h)
            if nh != h:
                en_changes.append((h, nh)); e["headword_en"] = nh; dirty = True
            # flag any headword that still carries an interior/standalone capital
            for w in WORD.findall(nh):
                if any(c.isupper() for c in w) and not (len(w) >= 2 and w.isupper()):
                    if w not in ("I",):
                        kept_caps.append((nh, w))
            for t in e.get("vi_terms", []):
                term = t.get("term", "")
                if "$$" in term:
                    math_terms.append(term); continue
                nt = normalize_vi(term)
                if nt != term:
                    vi_changes.append((term, nt)); t["term"] = nt; dirty = True
        if dirty and apply:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"EN headword changes: {len(en_changes)}")
    for a, b in en_changes:
        print(f"   {a!r:45} -> {b!r}")
    print(f"\nVI term changes: {len(vi_changes)}")
    for a, b in vi_changes[:60]:
        print(f"   {a!r:45} -> {b!r}")
    if len(vi_changes) > 60:
        print(f"   ... (+{len(vi_changes) - 60} more)")
    print(f"\nREVIEW — headwords keeping a capital (must all be proper nouns/symbols):")
    seen = set()
    for nh, w in kept_caps:
        if w not in seen:
            seen.add(w)
            print(f"   kept {w!r:16} e.g. {nh!r}")
    if math_terms:
        print(f"\nVI terms with math (skipped): {len(math_terms)}")
    print("\n" + ("APPLIED to JSON." if apply else "DRY-RUN (no files written). Re-run with --apply."))


if __name__ == "__main__":
    main()
