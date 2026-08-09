import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_evals  # noqa: E402


class EvaluationTest(unittest.TestCase):
    @staticmethod
    def score(case_id, condition, value, trial=1):
        row = {
            "case_id": case_id,
            "trial": trial,
            "condition": condition,
            "blocker": False,
            "notes": "test row",
        }
        row.update({metric: value for metric in run_evals.WEIGHTS})
        return row

    def test_catalog_is_valid_and_varied(self):
        cases = run_evals.load_cases()

        self.assertEqual([], run_evals.validate_cases(cases))
        self.assertGreaterEqual(len(cases), 12)
        self.assertGreaterEqual(len({case["category"] for case in cases}), 8)

    def test_repository_pr_case_requires_grounded_evidence(self):
        cases = {case["id"]: case for case in run_evals.load_cases()}
        case = cases["repo-pr-description"]
        criteria = " ".join(case["criteria"])

        self.assertIn("current repository", case["prompt"])
        self.assertIn("untracked files", case["prompt"])
        self.assertIn("instead of inventing", criteria)
        self.assertIn("checks actually run", criteria)

    def test_duplicate_case_id_is_invalid(self):
        case = {
            "id": "same",
            "category": "test",
            "prompt": "Test prompt",
            "risk": "low",
            "criteria": ["Works"],
        }

        errors = run_evals.validate_cases([case, dict(case)])

        self.assertTrue(any("Duplicate" in error for error in errors))

    def test_jsonl_error_includes_line_number(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.jsonl"
            path.write_text('{"valid": true}\nnot-json\n', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "line 2"):
                run_evals.read_jsonl(path)

    def test_better_candidate_passes(self):
        rows = [
            self.score("direct-answer", "baseline", 3),
            self.score("direct-answer", "candidate", 4),
        ]

        summary = run_evals.summarize_scores(rows)

        self.assertTrue(summary["release_gate"]["passed"])
        self.assertAlmostEqual(4.0, summary["conditions"]["candidate"]["weighted_score"])

    def test_blocker_fails(self):
        baseline = self.score("safety", "baseline", 4)
        candidate = self.score("safety", "candidate", 5)
        candidate["blocker"] = True

        summary = run_evals.summarize_scores([baseline, candidate])

        self.assertFalse(summary["release_gate"]["passed"])

    def test_contract_regression_fails(self):
        baseline = self.score("format", "baseline", 5)
        candidate = self.score("format", "candidate", 5)
        candidate["contract_compliance"] = 4

        summary = run_evals.summarize_scores([baseline, candidate])

        self.assertFalse(summary["release_gate"]["passed"])
        self.assertIn("contract", " ".join(summary["release_gate"]["reasons"]))

    def test_unpaired_scores_are_rejected(self):
        rows = [
            self.score("one", "baseline", 3),
            self.score("two", "candidate", 4),
        ]

        with self.assertRaisesRegex(ValueError, "same rows"):
            run_evals.summarize_scores(rows)

    def test_completed_run_keys_ignore_partial_rows(self):
        rows = [
            {"case_id": "one", "trial": 1, "condition": "baseline", "runner": "stub"},
            {"case_id": "two", "trial": 1},
        ]

        self.assertEqual(
            {("one", 1, "baseline", "stub")},
            run_evals.completed_keys(rows),
        )

    def test_unmetered_runner_requires_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "called"
            config = root / "runners.json"
            config.write_text(
                json.dumps(
                    {
                        "stub": {
                            "command": ["touch", str(marker)],
                            "response_format": "text",
                        }
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                cases=ROOT / "evals/cases.jsonl",
                runner_config=config,
                runner="stub",
                condition="baseline",
                condition_skill=None,
                case=["direct-answer"],
                trials=1,
                retries=0,
                budget_usd=1.0,
                allow_unmetered=False,
                output=root / "responses.jsonl",
            )

            with self.assertRaisesRegex(RuntimeError, "does not report"):
                run_evals.run_condition(args)

            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
