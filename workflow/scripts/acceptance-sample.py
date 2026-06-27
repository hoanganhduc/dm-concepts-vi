#!/usr/bin/env python3
"""Acceptance sampling for a measured, defensible book-wide error rate.

Instead of "we reviewed it", draw a reproducible random sample of entries,
review exactly those, count defects, and report a book-wide defect-rate estimate
with a 95% Wilson confidence interval (ISO 2859 acceptance-sampling idea, applied
as attribute sampling). Deterministic: the sample is chosen by hashing entry ids
(no RNG, so it is identical on every run and across machines) — change --salt to
draw an independent sample.

Two modes:
  draw   — print/save the sample to review (default N=80)
  report — given defects found in a sample of size N, print rate + 95% CI

Usage:
  acceptance-sample.py draw --n 80 --out /tmp/dm-improve/sample.json
  acceptance-sample.py draw --n 80 --salt run2
  acceptance-sample.py report --defects 3 --n 80
"""
import glob
import hashlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def arg(flag, default=None, cast=str):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


def load_pool():
    pool = []
    import yaml
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "terms", "entries-*.yaml"))):
        for e in (yaml.safe_load(open(f, encoding="utf-8")) or {}).get("entries", []):
            if e.get("see_ref"):
                continue
            rec = next((t["term"] for t in e.get("vi_terms", []) if t.get("recommended")), "")
            pool.append({"id": e["id"], "headword_en": e["headword_en"], "recommended": rec})
    return pool


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "draw"

    if mode == "report":
        n = arg("--n", 80, int)
        k = arg("--defects", 0, int)
        p, lo, hi = wilson(k, n)
        print(f"Sample: {k} defect(s) in {n} reviewed entries")
        print(f"Point estimate defect rate: {p:.1%}")
        print(f"95% Wilson CI: [{lo:.1%}, {hi:.1%}]")
        print(f"=> projected defective entries over 766 non-stub: "
              f"{round(p*766)} (95% CI {round(lo*766)}–{round(hi*766)})")
        return

    # draw
    n = arg("--n", 80, int)
    salt = arg("--salt", "v1")
    out = arg("--out")
    pool = load_pool()
    ranked = sorted(pool, key=lambda e: hashlib.md5((salt + ":" + e["id"]).encode()).hexdigest())
    sample = ranked[:n]
    print(f"Drew {len(sample)} of {len(pool)} non-stub entries (salt={salt!r}, deterministic).")
    print("Review each for any defect (wrong term / bad definition / wrong example / "
          "broken citation), count defects, then:")
    print(f"  acceptance-sample.py report --defects <k> --n {len(sample)}\n")
    for e in sample:
        print(f"  {e['id']:<34} {e['headword_en']:<30} {e['recommended']}")
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump({"n": len(sample), "salt": salt, "pool": len(pool), "sample": sample},
                  open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
