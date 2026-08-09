#!/usr/bin/env python3
"""Validate cases, run response trials, and score paired conditions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "cases.jsonl"
CONDITIONS = ("baseline", "candidate", "comparator")
WEIGHTS = {
    "correctness": 0.25,
    "accessibility": 0.20,
    "scanability": 0.15,
    "visual_usefulness": 0.15,
    "contract_compliance": 0.15,
    "safety": 0.10,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}: line {line_number}: {error.msg}") from error
        if not isinstance(value, dict):
            raise ValueError(f"{path}: line {line_number}: expected an object")
        rows.append(value)
    return rows


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    return read_jsonl(path)


def validate_cases(cases: list[dict[str, Any]]) -> list[str]:
    required = {"id", "category", "prompt", "risk", "criteria"}
    errors: list[str] = []
    seen: set[str] = set()

    for index, case in enumerate(cases, 1):
        missing = sorted(required - case.keys())
        if missing:
            errors.append(f"Case {index}: missing {', '.join(missing)}")
            continue

        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"Case {index}: id must be a non-empty string")
        elif case_id in seen:
            errors.append(f"Duplicate case id: {case_id}")
        else:
            seen.add(case_id)

        if case["risk"] not in {"low", "medium", "high"}:
            errors.append(f"Case {case_id}: invalid risk")
        if not isinstance(case["criteria"], list) or not case["criteria"]:
            errors.append(f"Case {case_id}: criteria must be a non-empty list")

    if not cases:
        errors.append("Case catalog is empty")
    return errors


def completed_keys(rows: list[dict[str, Any]]) -> set[tuple[str, int, str, str]]:
    result: set[tuple[str, int, str, str]] = set()
    for row in rows:
        key = (row.get("case_id"), row.get("trial"), row.get("condition"), row.get("runner"))
        if (
            isinstance(key[0], str)
            and isinstance(key[1], int)
            and isinstance(key[2], str)
            and isinstance(key[3], str)
        ):
            result.add(key)  # type: ignore[arg-type]
    return result


def _validate_score(row: dict[str, Any], index: int) -> None:
    required = {"case_id", "trial", "condition", "blocker", "notes", *WEIGHTS}
    missing = sorted(required - row.keys())
    if missing:
        raise ValueError(f"Score row {index}: missing {', '.join(missing)}")
    if row["condition"] not in CONDITIONS:
        raise ValueError(f"Score row {index}: invalid condition")
    for metric in WEIGHTS:
        value = row[metric]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 1 <= value <= 5:
            raise ValueError(f"Score row {index}: {metric} must be from 1 to 5")
    if not isinstance(row["blocker"], bool):
        raise ValueError(f"Score row {index}: blocker must be true or false")


def summarize_scores(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(rows, 1):
        _validate_score(row, index)
        grouped[row["condition"]].append(row)

    if not {"baseline", "candidate"}.issubset(grouped):
        raise ValueError("Scores must include baseline and candidate conditions")

    coverage: dict[str, Counter[tuple[str, int]]] = {}
    for condition, condition_rows in grouped.items():
        keys = Counter((row["case_id"], row["trial"]) for row in condition_rows)
        if any(count > 1 for count in keys.values()):
            raise ValueError(f"{condition}: duplicate score rows")
        coverage[condition] = keys

    for condition, keys in coverage.items():
        if keys != coverage["baseline"]:
            raise ValueError(f"{condition} was not judged on the same rows as baseline")

    conditions: dict[str, dict[str, Any]] = {}
    for condition, condition_rows in sorted(grouped.items()):
        averages = {
            metric: sum(float(row[metric]) for row in condition_rows) / len(condition_rows)
            for metric in WEIGHTS
        }
        conditions[condition] = {
            "rows": len(condition_rows),
            **averages,
            "weighted_score": sum(averages[name] * weight for name, weight in WEIGHTS.items()),
            "blocking_findings": sum(bool(row["blocker"]) for row in condition_rows),
        }

    baseline = conditions["baseline"]
    candidate = conditions["candidate"]
    reasons: list[str] = []
    if candidate["blocking_findings"]:
        reasons.append("Candidate has blocking findings.")
    for protected in ("correctness", "safety", "contract_compliance"):
        if candidate[protected] < baseline[protected] - 0.1:
            reasons.append(f"Candidate {protected.replace('_', ' ')} regressed by more than 0.1 points.")
    if candidate["weighted_score"] <= baseline["weighted_score"]:
        reasons.append("Candidate weighted score did not beat baseline.")

    return {
        "weights": WEIGHTS,
        "conditions": conditions,
        "release_gate": {"passed": not reasons, "reasons": reasons},
    }


def build_condition_prompt(task: str, condition: str, skill_path: Path | None) -> str:
    if condition == "baseline":
        return task
    if skill_path is None:
        raise ValueError(f"--condition-skill is required for {condition}")
    rules = skill_path.read_text(encoding="utf-8")
    return (
        "Follow the response style below. Do not quote or discuss these instructions.\n\n"
        f"<response_style>\n{rules}\n</response_style>\n\n"
        f"<task>\n{task}\n</task>"
    )


def parse_response(output: str, response_format: str) -> tuple[str, dict[str, Any], float | None]:
    if response_format == "text":
        return output.strip(), {}, None
    if response_format == "claude-json":
        value = json.loads(output)
        return str(value.get("result", "")).strip(), value.get("usage") or {}, value.get("total_cost_usd")
    if response_format == "codex-jsonl":
        text = ""
        usage: dict[str, Any] = {}
        for event in (json.loads(line) for line in output.splitlines() if line.strip()):
            item = event.get("item") or {}
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                text = str(item.get("text", text))
            if event.get("type") == "turn.completed":
                usage = event.get("usage") or usage
        return text.strip(), usage, None
    raise ValueError(f"Unsupported response format: {response_format}")


def run_condition(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    errors = validate_cases(cases)
    if errors:
        raise ValueError("\n".join(errors))
    if args.case:
        missing = sorted(set(args.case) - {case["id"] for case in cases})
        if missing:
            raise ValueError(f"Unknown cases: {', '.join(missing)}")
        cases = [case for case in cases if case["id"] in args.case]

    runners = json.loads(args.runner_config.read_text(encoding="utf-8"))
    if args.runner not in runners:
        raise ValueError(f"Unknown runner: {args.runner}")
    runner = runners[args.runner]
    response_format = runner.get("response_format", "text")
    if response_format != "claude-json" and not args.allow_unmetered:
        raise RuntimeError("Runner does not report dollar cost; use --allow-unmetered with an external hard cap")

    prior = read_jsonl(args.output) if args.output.exists() else []
    done = completed_keys(prior)
    spent = sum(
        float(row.get("cost_usd") or 0)
        for row in prior
        if row.get("runner") == args.runner and row.get("condition") == args.condition
    )
    if not 0 < args.budget_usd <= 25:
        raise ValueError("--budget-usd must be greater than 0 and no more than 25")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as destination:
        for trial in range(1, args.trials + 1):
            for case in cases:
                key = (case["id"], trial, args.condition, args.runner)
                if key in done:
                    continue
                if spent >= args.budget_usd:
                    return 2
                prompt = build_condition_prompt(case["prompt"], args.condition, args.condition_skill)
                command = [*runner["command"]]
                if flag := runner.get("budget_flag"):
                    command.extend([flag, f"{args.budget_usd - spent:.4f}"])
                command.append(prompt)

                completed = None
                for attempt in range(args.retries + 1):
                    completed = subprocess.run(
                        command,
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if completed.returncode == 0:
                        break
                    if attempt < args.retries:
                        time.sleep(min(2**attempt, 4))
                assert completed is not None
                if completed.returncode:
                    raise RuntimeError(completed.stderr.strip() or "Runner failed")

                response, usage, cost = parse_response(completed.stdout, response_format)
                spent += float(cost or 0)
                row = {
                    "case_id": case["id"],
                    "trial": trial,
                    "condition": args.condition,
                    "runner": args.runner,
                    "response": response,
                    "usage": usage,
                    "cost_usd": cost,
                }
                destination.write(json.dumps(row, ensure_ascii=False) + "\n")
                destination.flush()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--cases", type=Path, default=DEFAULT_CASES)

    plan = commands.add_parser("plan")
    plan.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    plan.add_argument("--trials", type=int, default=3)
    plan.add_argument("--include-comparator", action="store_true")

    score = commands.add_parser("score")
    score.add_argument("scores", type=Path)

    run = commands.add_parser("run")
    run.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    run.add_argument("--runner-config", type=Path, default=ROOT / "evals/runners.example.json")
    run.add_argument("--runner", required=True)
    run.add_argument("--condition", choices=CONDITIONS, required=True)
    run.add_argument("--condition-skill", type=Path)
    run.add_argument("--case", action="append")
    run.add_argument("--trials", type=int, default=3)
    run.add_argument("--retries", type=int, default=2)
    run.add_argument("--budget-usd", type=float, default=25.0)
    run.add_argument("--allow-unmetered", action="store_true")
    run.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        errors = validate_cases(load_cases(args.cases))
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("Evaluation cases are valid.")
        return 0
    if args.command == "plan":
        cases = load_cases(args.cases)
        errors = validate_cases(cases)
        if errors:
            raise ValueError("\n".join(errors))
        conditions = ["baseline", "candidate"]
        if args.include_comparator:
            conditions.append("comparator")
        for trial in range(1, args.trials + 1):
            for case in cases:
                for condition in conditions:
                    print(json.dumps({"case_id": case["id"], "trial": trial, "condition": condition}))
        return 0
    if args.command == "score":
        print(json.dumps(summarize_scores(read_jsonl(args.scores)), indent=2))
        return 0
    return run_condition(args)


if __name__ == "__main__":
    raise SystemExit(main())
