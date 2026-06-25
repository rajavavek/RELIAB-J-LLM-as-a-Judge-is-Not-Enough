#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reliabj.metrics import reliability_profile


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.ledger)
    profile = reliability_profile(df)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(profile["profiles"]).to_csv(out, index=False)
    domain_out = out.with_name(out.stem + "_domain_accuracy.csv")
    pd.DataFrame([{"domain": k, "accuracy": v} for k, v in profile["domain_accuracy"].items()]).to_csv(domain_out, index=False)
    print(f"Wrote profile to {out}")
    print(f"Wrote domain accuracy to {domain_out}")


if __name__ == "__main__":
    main()
