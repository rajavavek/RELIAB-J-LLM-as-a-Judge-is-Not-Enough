#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reliabj.bootstrap import bootstrap_ci
from reliabj import metrics

METRICS = {
    "accuracy": metrics.accuracy,
    "ece": metrics.expected_calibration_error,
    "domain_gap": metrics.domain_gap,
    "asr": metrics.attack_success_rate,
    "robustness": metrics.robustness,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--metric", choices=sorted(METRICS), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--iterations", type=int, default=2000)
    args = ap.parse_args()
    df = pd.read_csv(args.ledger)
    rows = []
    for model, g in df.groupby("judge_model"):
        est, lo, hi = bootstrap_ci(g, METRICS[args.metric], iterations=args.iterations)
        rows.append({"judge_model": model, "metric": args.metric, "estimate": est, "ci_lower": lo, "ci_upper": hi})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote bootstrap CI to {out}")


if __name__ == "__main__":
    main()
