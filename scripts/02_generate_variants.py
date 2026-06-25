#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reliabj.io import load_jsonl, write_jsonl
from reliabj.perturbations import generate_variants, PERTURBATION_FUNCS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--perturbations", default=",".join(PERTURBATION_FUNCS.keys()))
    args = ap.parse_args()
    names = [x.strip() for x in args.perturbations.split(',') if x.strip()]
    items = load_jsonl(args.items)
    variants = []
    for item in items:
        variants.extend(generate_variants(item, names))
    write_jsonl(variants, args.out)
    print(f"Wrote {len(variants)} variants to {args.out}")


if __name__ == "__main__":
    main()
