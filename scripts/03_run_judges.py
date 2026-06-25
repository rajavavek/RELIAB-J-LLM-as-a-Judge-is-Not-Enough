#!/usr/bin/env python
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import uuid
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reliabj.io import load_jsonl
from reliabj.ledger import write_ledger
from reliabj.judges import HeuristicDemoJudge, OpenAIJudge, AnthropicJudge
from reliabj.prompts import load_template, render_pairwise_prompt
from reliabj.parsers import parse_pairwise_output


def count_tokens(text: str) -> int:
    return len(str(text).split())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--judge", choices=["demo", "openai", "anthropic"], default="demo")
    ap.add_argument("--model", default="heuristic-demo-judge")
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--prompt-template", default="data/prompts/pairwise_judge_v1.txt")
    ap.add_argument("--system-prompt", default="data/prompts/system_judge.txt")
    args = ap.parse_args()

    variants = load_jsonl(args.variants)
    run_id = os.environ.get("RELIABJ_RUN_ID", str(uuid.uuid4()))
    template = load_template(args.prompt_template)
    system_prompt = load_template(args.system_prompt)

    if args.judge == "demo":
        judge = HeuristicDemoJudge()
        model_name = judge.name
    elif args.judge == "openai":
        judge = OpenAIJudge(model=args.model)
        model_name = args.model
    else:
        judge = AnthropicJudge(model=args.model)
        model_name = args.model

    rows = []
    for run_index in range(args.runs):
        for item in variants:
            prompt = render_pairwise_prompt(item, template)
            if args.judge == "demo":
                result = judge.judge_pairwise(item)
            else:
                result = judge.judge(system_prompt, prompt)
            try:
                parsed = parse_pairwise_output(result.raw_output)
                parsed_label = parsed["parsed_label"]
                confidence = parsed["confidence"]
                rationale = parsed["rationale"]
            except Exception as exc:
                parsed_label = "parse_error"
                confidence = 0.0
                rationale = f"parse_error: {exc}"
            responses = item.get("responses", {})
            rows.append({
                "run_id": run_id,
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "judge_model": model_name,
                "judge_mode": "pair",
                "item_id": item.get("item_id"),
                "base_item_id": item.get("base_item_id", item.get("item_id")),
                "variant_id": item.get("variant_id", item.get("item_id")),
                "domain": item.get("domain"),
                "perturbation": item.get("perturbation", "identity"),
                "run_index": run_index,
                "raw_output": result.raw_output,
                "parsed_label": parsed_label,
                "confidence": confidence,
                "rationale": rationale,
                "latency_ms": result.latency_ms,
                "token_count": result.token_count,
                "cost_usd": result.cost_usd,
                "gold_label": item.get("gold_label"),
                "response_a_tokens": count_tokens(responses.get("A", "")),
                "response_b_tokens": count_tokens(responses.get("B", "")),
            })
    write_ledger(rows, args.out)
    print(f"Wrote {len(rows)} judge executions to {args.out}")


if __name__ == "__main__":
    main()
