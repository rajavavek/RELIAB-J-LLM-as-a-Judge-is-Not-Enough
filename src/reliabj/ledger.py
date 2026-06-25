from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Any, Iterable, List

LEDGER_COLUMNS = [
    "run_id", "timestamp", "judge_model", "judge_mode", "item_id", "base_item_id",
    "variant_id", "domain", "perturbation", "run_index", "raw_output", "parsed_label",
    "confidence", "rationale", "latency_ms", "token_count", "cost_usd", "gold_label",
    "response_a_tokens", "response_b_tokens"
]


def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {col: row.get(col, "") for col in LEDGER_COLUMNS}


def write_ledger(rows: Iterable[Dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(normalize_row(row))
