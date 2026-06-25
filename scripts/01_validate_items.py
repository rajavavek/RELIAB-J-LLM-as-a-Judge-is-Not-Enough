#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reliabj.io import load_jsonl
from reliabj.schema import validate_items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    args = ap.parse_args()
    items = load_jsonl(args.items)
    errors = validate_items(items)
    if errors:
        for item_id, errs in errors.items():
            print(item_id, "; ".join(errs))
        raise SystemExit(1)
    print(f"OK: {len(items)} items validated from {args.items}")


if __name__ == "__main__":
    main()
