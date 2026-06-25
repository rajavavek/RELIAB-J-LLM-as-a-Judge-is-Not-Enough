from __future__ import annotations

from typing import Dict, Any, List

REQUIRED_FIELDS = [
    "item_id", "domain", "task_type", "prompt", "responses", "rubric", "gold_label", "evidence"
]
VALID_DOMAINS = {
    "factual_qa", "math", "code", "summarization", "safety", "rag",
    "medical_legal", "instruction_following", "creative_writing", "agent"
}
VALID_TASK_TYPES = {"pairwise", "scalar", "binary"}


def validate_item(item: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in item:
            errors.append(f"missing required field: {field}")
    if item.get("domain") not in VALID_DOMAINS:
        errors.append(f"invalid domain: {item.get('domain')}")
    if item.get("task_type") not in VALID_TASK_TYPES:
        errors.append(f"invalid task_type: {item.get('task_type')}")
    if item.get("task_type") == "pairwise":
        responses = item.get("responses", {})
        if not isinstance(responses, dict) or "A" not in responses or "B" not in responses:
            errors.append("pairwise items require responses.A and responses.B")
        if str(item.get("gold_label")) not in {"A", "B", "tie"}:
            errors.append("pairwise gold_label must be A, B, or tie")
    return errors


def validate_items(items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    report: Dict[str, List[str]] = {}
    seen = set()
    for item in items:
        item_id = str(item.get("item_id", "<missing>"))
        errs = validate_item(item)
        if item_id in seen:
            errs.append("duplicate item_id")
        seen.add(item_id)
        if errs:
            report[item_id] = errs
    return report
