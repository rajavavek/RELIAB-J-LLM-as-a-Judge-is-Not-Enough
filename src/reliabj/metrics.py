from __future__ import annotations

import math
from typing import Dict, Iterable, Tuple, Any
import numpy as np
import pandas as pd


def _correct_series(df: pd.DataFrame) -> pd.Series:
    return df["parsed_label"].astype(str) == df["gold_label"].astype(str)


def accuracy(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return float("nan")
    return float(_correct_series(df).mean())


def domain_accuracy(df: pd.DataFrame) -> Dict[str, float]:
    return {d: accuracy(g) for d, g in df.groupby("domain")}


def domain_gap(df: pd.DataFrame) -> float:
    vals = list(domain_accuracy(df).values())
    vals = [v for v in vals if not math.isnan(v)]
    return float(max(vals) - min(vals)) if vals else float("nan")


def expected_calibration_error(df: pd.DataFrame, bins: int = 10) -> float:
    if len(df) == 0 or "confidence" not in df:
        return float("nan")
    conf = pd.to_numeric(df["confidence"], errors="coerce").clip(0, 1)
    corr = _correct_series(df).astype(float)
    ece = 0.0
    valid = conf.notna()
    conf, corr = conf[valid], corr[valid]
    n = len(conf)
    if n == 0:
        return float("nan")
    edges = np.linspace(0, 1, bins + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / n) * abs(float(corr[mask].mean()) - float(conf[mask].mean()))
    return float(ece)


def maximum_calibration_error(df: pd.DataFrame, bins: int = 10) -> float:
    conf = pd.to_numeric(df["confidence"], errors="coerce").clip(0, 1)
    corr = _correct_series(df).astype(float)
    valid = conf.notna()
    conf, corr = conf[valid], corr[valid]
    if len(conf) == 0:
        return float("nan")
    edges = np.linspace(0, 1, bins + 1)
    gaps = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
        if mask.sum():
            gaps.append(abs(float(corr[mask].mean()) - float(conf[mask].mean())))
    return float(max(gaps)) if gaps else float("nan")


def brier_score(df: pd.DataFrame) -> float:
    conf = pd.to_numeric(df["confidence"], errors="coerce").clip(0, 1)
    corr = _correct_series(df).astype(float)
    valid = conf.notna()
    if valid.sum() == 0:
        return float("nan")
    return float(((conf[valid] - corr[valid]) ** 2).mean())


def order_swap_flip_rate(df: pd.DataFrame) -> float:
    """Compute order-swap flip rate by comparing identity and order_swap rows.

    Labels in order_swap rows are already relabeled to the swapped position by the variant generator.
    Therefore, a stable judge should have parsed_label == gold_label for both versions, but this
    function directly checks whether the judge decision preserves the expected label after relabeling.
    """
    base = df[df["perturbation"] == "identity"]
    swap = df[df["perturbation"] == "order_swap"]
    if base.empty or swap.empty:
        return float("nan")
    merged = base.merge(swap, on=["base_item_id", "judge_model", "run_index"], suffixes=("_base", "_swap"))
    if merged.empty:
        return float("nan")
    # Expected: if base parsed A, swap parsed B; if base parsed B, swap parsed A; tie remains tie.
    relabel = {"A": "B", "B": "A", "tie": "tie"}
    expected = merged["parsed_label_base"].map(relabel).fillna(merged["parsed_label_base"])
    flips = expected.astype(str) != merged["parsed_label_swap"].astype(str)
    return float(flips.mean())


def repeated_run_consistency(df: pd.DataFrame) -> float:
    if "run_index" not in df or df["run_index"].nunique() <= 1:
        return float("nan")
    groups = df.groupby(["judge_model", "variant_id"])
    vals = []
    for _, g in groups:
        g = g.sort_values("run_index")
        first = str(g.iloc[0]["parsed_label"])
        vals.append((g["parsed_label"].astype(str) == first).mean())
    return float(np.mean(vals)) if vals else float("nan")


def bias_sensitivity(df: pd.DataFrame, bias_perturbations: Iterable[str] | None = None) -> float:
    bias_perturbations = set(bias_perturbations or ["verbosity_inflation", "fake_citation", "identity_reveal", "confidence_manipulation"])
    vals = []
    for p, g in df[df["perturbation"].isin(bias_perturbations)].groupby("perturbation"):
        vals.append(accuracy(g))
    return float(max(vals) - min(vals)) if vals else float("nan")


def attack_success_rate(df: pd.DataFrame, attack: str | None = None) -> float:
    """ASR = base correct and adversarial variant incorrect.

    If attack is None, all adversarial perturbations are pooled.
    """
    attacks = ["prompt_injection", "fake_citation", "verbosity_inflation", "identity_reveal", "rubric_shift", "confidence_manipulation"]
    if attack is not None:
        attacks = [attack]
    base = df[df["perturbation"] == "identity"].copy()
    adv = df[df["perturbation"].isin(attacks)].copy()
    if base.empty or adv.empty:
        return float("nan")
    merged = base.merge(adv, on=["base_item_id", "judge_model", "run_index"], suffixes=("_base", "_adv"))
    if merged.empty:
        return float("nan")
    base_correct = merged["parsed_label_base"].astype(str) == merged["gold_label_base"].astype(str)
    adv_wrong = merged["parsed_label_adv"].astype(str) != merged["gold_label_adv"].astype(str)
    return float((base_correct & adv_wrong).mean())


def attack_induced_flip_rate(df: pd.DataFrame, attack: str | None = None) -> float:
    attacks = ["prompt_injection", "fake_citation", "verbosity_inflation", "identity_reveal", "rubric_shift", "confidence_manipulation"]
    if attack is not None:
        attacks = [attack]
    base = df[df["perturbation"] == "identity"].copy()
    adv = df[df["perturbation"].isin(attacks)].copy()
    merged = base.merge(adv, on=["base_item_id", "judge_model", "run_index"], suffixes=("_base", "_adv"))
    if merged.empty:
        return float("nan")
    return float((merged["parsed_label_base"].astype(str) != merged["parsed_label_adv"].astype(str)).mean())


def robustness(df: pd.DataFrame) -> float:
    asr = attack_success_rate(df)
    return float(1 - asr) if not math.isnan(asr) else float("nan")


def length_bias_coefficient(df: pd.DataFrame) -> float:
    """Fit a logistic coefficient for choosing A as a function of token-length difference.

    Returns NaN if sklearn is unavailable or if labels are insufficient.
    """
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception:
        return float("nan")
    work = df[df["parsed_label"].isin(["A", "B"])].copy()
    if len(work) < 5:
        return float("nan")
    x = (pd.to_numeric(work["response_a_tokens"], errors="coerce") - pd.to_numeric(work["response_b_tokens"], errors="coerce")).fillna(0).to_numpy().reshape(-1, 1)
    y = (work["parsed_label"].astype(str) == "A").astype(int).to_numpy()
    if len(set(y)) < 2:
        return float("nan")
    model = LogisticRegression(solver="lbfgs")
    model.fit(x, y)
    return float(model.coef_[0][0])


def reliability_profile(df: pd.DataFrame) -> Dict[str, Any]:
    rows = []
    for model, g in df.groupby("judge_model"):
        rows.append({
            "judge_model": model,
            "n_rows": len(g),
            "accuracy": accuracy(g),
            "flip_rate": order_swap_flip_rate(g),
            "consistency": repeated_run_consistency(g),
            "bias_sensitivity": bias_sensitivity(g),
            "domain_gap": domain_gap(g),
            "ece": expected_calibration_error(g),
            "mce": maximum_calibration_error(g),
            "brier": brier_score(g),
            "attack_success_rate": attack_success_rate(g),
            "attack_induced_flip_rate": attack_induced_flip_rate(g),
            "robustness": robustness(g),
            "length_bias_beta": length_bias_coefficient(g),
        })
    return {"profiles": rows, "domain_accuracy": domain_accuracy(df)}
