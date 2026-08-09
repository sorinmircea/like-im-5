# Evaluations

The harness compares response quality, not just response length. Cases live in `cases.jsonl`; the scoring contract lives in `rubric.md`.

## Validate and plan

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

## Run paired conditions

Copy `runners.example.json` to the ignored `runners.json` if you need local changes. Keep the model, cases, and trial count the same for both conditions.

```bash
python3 scripts/run_evals.py run \
  --runner claude \
  --condition baseline \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl

python3 scripts/run_evals.py run \
  --runner claude \
  --condition candidate \
  --condition-skill skills/like-im-5/SKILL.md \
  --trials 3 \
  --budget-usd 12.50 \
  --output evals/results/responses.jsonl
```

Runs resume from completed rows. Runners without cost reporting require `--allow-unmetered`; use it only when the provider account has a separate hard cap.

### Run with Codex

The example runner starts Codex with user configuration disabled and a read-only sandbox. This keeps installed skills and workspace write access from leaking into the comparison.

```bash
python3 scripts/run_evals.py run \
  --runner codex \
  --condition baseline \
  --trials 3 \
  --allow-unmetered \
  --output evals/results/responses.jsonl

python3 scripts/run_evals.py run \
  --runner codex \
  --condition candidate \
  --condition-skill skills/like-im-5/SKILL.md \
  --trials 3 \
  --allow-unmetered \
  --output evals/results/responses.jsonl
```

The Codex JSONL runner does not report dollar cost, so the harness cannot enforce `--budget-usd`. Use an account-level limit before passing `--allow-unmetered`.

For a repository-backed smoke test, run the case that asks Codex to inspect this codebase and draft its PR description:

```bash
python3 scripts/run_evals.py run \
  --runner codex \
  --condition candidate \
  --condition-skill skills/like-im-5/SKILL.md \
  --case repo-pr-description \
  --trials 1 \
  --allow-unmetered \
  --output evals/results/smoke.jsonl
```

The evaluation runner always starts the model from the repository root. The case includes untracked files in the simulated PR and requires the description to use only repository evidence.

## Judge and score

Blind the condition before judging. Write one JSON object per response with every field from `rubric.md`, plus `case_id`, `trial`, `condition`, `blocker`, and `notes`.

```bash
python3 scripts/run_evals.py score evals/results/scores.jsonl
```

Do not compare runs produced with different cases, models, trial counts, or rubrics.
