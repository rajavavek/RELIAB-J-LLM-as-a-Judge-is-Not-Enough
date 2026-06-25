from __future__ import annotations

import json
import re
from typing import Any, Dict


def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON object found in judge output")


def parse_pairwise_output(text: str) -> Dict[str, Any]:
    """Parse a judge output into winner/confidence/rationale.

    The parser accepts valid JSON first and then falls back to conservative regex extraction.
    """
    try:
        obj = _extract_json(text)
        winner = str(obj.get("winner", obj.get("label", ""))).strip().lower()
        winner = {"a": "A", "b": "B", "tie": "tie"}.get(winner, winner)
        if winner not in {"A", "B", "tie"}:
            raise ValueError(f"Invalid winner: {winner}")
        confidence = float(obj.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        return {"parsed_label": winner, "confidence": confidence, "rationale": str(obj.get("rationale", ""))}
    except Exception:
        # Conservative fallback: only parse obvious labels.
        label_match = re.search(r"\b(winner|label|answer)\s*[:=]\s*['\"]?(A|B|tie)\b", text, flags=re.I)
        if not label_match:
            raise
        conf_match = re.search(r"\bconfidence\s*[:=]\s*([01](?:\.\d+)?)", text, flags=re.I)
        confidence = float(conf_match.group(1)) if conf_match else 0.5
        return {"parsed_label": label_match.group(2).upper() if label_match.group(2).lower() != "tie" else "tie", "confidence": max(0.0, min(1.0, confidence)), "rationale": "regex_fallback"}


def parse_scalar_output(text: str) -> Dict[str, Any]:
    obj = _extract_json(text)
    score = int(obj.get("score", obj.get("overall_score")))
    if not 1 <= score <= 5:
        raise ValueError(f"Invalid score: {score}")
    confidence = max(0.0, min(1.0, float(obj.get("confidence", 0.5))))
    return {"parsed_label": score, "confidence": confidence, "rationale": str(obj.get("rationale", ""))}
