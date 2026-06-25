from __future__ import annotations

from typing import Callable, Tuple
import numpy as np
import pandas as pd


def bootstrap_ci(df: pd.DataFrame, metric_fn: Callable[[pd.DataFrame], float], iterations: int = 2000, alpha: float = 0.05, seed: int = 2026) -> Tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    if df.empty:
        return float("nan"), float("nan"), float("nan")
    values = []
    idx = np.arange(len(df))
    for _ in range(iterations):
        sample_idx = rng.choice(idx, size=len(idx), replace=True)
        sample = df.iloc[sample_idx]
        values.append(metric_fn(sample))
    values = np.array([v for v in values if not np.isnan(v)], dtype=float)
    if len(values) == 0:
        return float("nan"), float("nan"), float("nan")
    estimate = metric_fn(df)
    lower = float(np.quantile(values, alpha / 2))
    upper = float(np.quantile(values, 1 - alpha / 2))
    return float(estimate), lower, upper
