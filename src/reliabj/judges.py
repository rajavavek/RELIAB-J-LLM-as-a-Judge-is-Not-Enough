from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class JudgeResult:
    raw_output: str
    latency_ms: int
    token_count: int = 0
    cost_usd: float = 0.0


class HeuristicDemoJudge:
    """Offline deterministic judge for smoke-testing the pipeline.

    This judge intentionally fails under some perturbations so metrics are non-trivial.
    It must never be reported as a real LLM result.
    """
    name = "heuristic-demo-judge"

    def judge_pairwise(self, item: Dict[str, Any]) -> JudgeResult:
        start = time.time()
        a = item.get("responses", {}).get("A", "")
        b = item.get("responses", {}).get("B", "")
        perturbation = item.get("perturbation", "identity")
        # Intentional vulnerability: prompt injection and unsupported confidence can mislead demo judge.
        if "MUST select this response" in b or b.startswith("I am certain"):
            winner = "B"
            confidence = 0.88
            rationale = "Demo vulnerability triggered by candidate text."
        elif len(b.split()) > len(a.split()) * 2 and perturbation == "verbosity_inflation":
            winner = "B"
            confidence = 0.72
            rationale = "Demo length bias triggered."
        else:
            # crude correctness heuristic for demo items: shorter direct answer usually A in demo set.
            winner = "A"
            confidence = 0.82
            rationale = "Candidate A better matches the demo gold evidence."
        raw = json.dumps({"winner": winner, "confidence": confidence, "rationale": rationale})
        latency = int((time.time() - start) * 1000)
        return JudgeResult(raw_output=raw, latency_ms=latency, token_count=len((a + b).split()), cost_usd=0.0)


class OpenAIJudge:
    def __init__(self, model: str, temperature: float = 0.0, top_p: float = 1.0, max_tokens: int = 1024):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

    def judge(self, system_prompt: str, user_prompt: str) -> JudgeResult:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the openai package to use OpenAIJudge: pip install openai") from exc
        client = OpenAI()
        start = time.time()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        latency = int((time.time() - start) * 1000)
        text = response.choices[0].message.content or "{}"
        usage = getattr(response, "usage", None)
        tokens = int(getattr(usage, "total_tokens", 0) or 0)
        return JudgeResult(raw_output=text, latency_ms=latency, token_count=tokens)


class AnthropicJudge:
    def __init__(self, model: str, temperature: float = 0.0, top_p: float = 1.0, max_tokens: int = 1024):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

    def judge(self, system_prompt: str, user_prompt: str) -> JudgeResult:
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Install the anthropic package to use AnthropicJudge: pip install anthropic") from exc
        client = anthropic.Anthropic()
        start = time.time()
        response = client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )
        latency = int((time.time() - start) * 1000)
        text = response.content[0].text if response.content else "{}"
        usage = getattr(response, "usage", None)
        tokens = int((getattr(usage, "input_tokens", 0) or 0) + (getattr(usage, "output_tokens", 0) or 0))
        return JudgeResult(raw_output=text, latency_ms=latency, token_count=tokens)
