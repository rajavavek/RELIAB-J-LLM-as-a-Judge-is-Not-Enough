from __future__ import annotations

from pathlib import Path
from typing import Dict, Any


def load_template(path: str | Path) -> str:
    return Path(path).read_text(encoding='utf-8')


def render_pairwise_prompt(item: Dict[str, Any], template: str) -> str:
    responses = item.get("responses", {})
    return template.format(
        prompt=item.get("prompt", ""),
        context=item.get("context") or "No additional context.",
        rubric=item.get("rubric", ""),
        response_a=responses.get("A", ""),
        response_b=responses.get("B", ""),
    )
