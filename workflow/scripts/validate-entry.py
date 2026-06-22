#!/usr/bin/env python3
"""Validate data/terms/*.yaml against the entry schema (docs/PLAN.md §3).

This is the precursor of the build-gate: every entry must pass before its
PreTeXt is merged. Errors fail the build (exit 1); warnings do not.

Checks:
  - required fields present (id, letter, headword_en, definition_vi, vi_terms);
  - id is kebab-case and unique;
  - letter matches the headword's first letter;
  - each vi_terms[].source_id exists in data/sources/registry.yaml;
  - exactly-one (or zero) recommended variant per entry;
  - status in {draft, verified, panel-approved};
  - verified/panel-approved entries must have a non-empty page for every variant
    (a draft may leave page empty -> warning only).
"""
import glob
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_STATUS = {"draft", "verified", "panel-approved"}

errors: list[str] = []
warnings: list[str] = []


def load_registry_ids() -> set:
    path = os.path.join(ROOT, "data", "sources", "registry.yaml")
    with open(path, encoding="utf-8") as fh:
        reg = yaml.safe_load(fh) or {}
    return {s["biblio_id"] for s in reg.get("sources", []) if s.get("biblio_id")}


def main() -> int:
    source_ids = load_registry_ids()
    all_ids = {e["id"] for f in glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))
               for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", []) if e.get("id")}
    seen_ids: dict[str, str] = {}
    n_entries = 0

    for path in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        for e in doc.get("entries", []):
            n_entries += 1
            eid = e.get("id", "<missing id>")
            where = f"{rel}:{eid}"

            is_stub = bool(e.get("see_ref"))
            req = (["id", "letter", "headword_en"] if is_stub
                   else ["id", "letter", "headword_en", "definition_vi", "vi_terms"])
            for field in req:
                if not e.get(field):
                    errors.append(f"{where}: missing required field '{field}'")
            if is_stub and e.get("see_ref") not in all_ids:
                errors.append(f"{where}: see_ref '{e.get('see_ref')}' not found among entries")

            if e.get("id"):
                if not KEBAB.match(e["id"]):
                    errors.append(f"{where}: id is not kebab-case")
                if e["id"] in seen_ids:
                    errors.append(f"{where}: duplicate id (also in {seen_ids[e['id']]})")
                seen_ids[e["id"]] = where

            hw, letter = e.get("headword_en", ""), str(e.get("letter", "")).upper()
            if hw and letter and hw[:1].upper() != letter:
                errors.append(f"{where}: letter '{letter}' != headword initial '{hw[:1].upper()}'")

            status = e.get("status", "draft")
            if status not in VALID_STATUS:
                errors.append(f"{where}: invalid status '{status}'")

            if is_stub:
                continue

            recommended = 0
            for t in e.get("vi_terms", []) or []:
                term = t.get("term")
                if not term:
                    errors.append(f"{where}: a vi_term has no 'term'")
                sid = t.get("source_id")
                page = str(t.get("page", "")).strip()
                verified = bool(t.get("verified"))
                if t.get("recommended"):
                    recommended += 1
                if verified:
                    # A verified citation must carry a real source + page.
                    if not sid:
                        errors.append(f"{where}: verified vi_term '{term}' has no source_id")
                    elif sid not in source_ids:
                        errors.append(f"{where}: source_id '{sid}' not in registry")
                    if not page:
                        errors.append(f"{where}: verified vi_term '{term}' has empty page")
                else:
                    # Unverified term: source/page must be absent (no fabrication).
                    if sid and sid not in source_ids:
                        errors.append(f"{where}: source_id '{sid}' not in registry")
                    if page:
                        warnings.append(f"{where}: unverified vi_term '{term}' has a page (should be empty)")
            if recommended != 1:
                errors.append(f"{where}: must have exactly one 'recommended' vi_term (found {recommended})")

    for w in warnings:
        print(f"WARN  {w}")
    for er in errors:
        print(f"ERROR {er}")
    print(f"\nValidated {n_entries} entries: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
