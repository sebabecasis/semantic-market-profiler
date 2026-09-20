from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from semantic_market_profiler.config import load_config, signals_from
from semantic_market_profiler.engine import build_profiles, extract_evidence, query_evidence
from semantic_market_profiler.models import Passage
from semantic_market_profiler.pipeline import build_plan, run_profile


ROOT = Path(__file__).resolve().parents[1]
HIRING = ROOT / "examples" / "hiring-philosophy"
BUYER = ROOT / "examples" / "buyer-readiness"


def passages(path: Path) -> list[Passage]:
    return [Passage.from_dict(row) for row in json.loads(path.read_text())]


class SemanticMarketProfilerTest(unittest.TestCase):
    def test_plan_waits_for_operator_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plan = build_plan(HIRING / "config.json", Path(temp))
            self.assertEqual(plan["status"], "pending_operator_review")
            self.assertTrue((Path(temp) / "source-plan.json").exists())

    def test_run_requires_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(PermissionError):
                run_profile(HIRING / "config.json", HIRING / "corpus.json", Path(temp))

    def test_hiring_profile_retains_exact_evidence(self) -> None:
        config = load_config(HIRING / "config.json")
        evidence = extract_evidence(passages(HIRING / "corpus.json"), signals_from(config))
        profiles = build_profiles(evidence, config["qualification"])
        kestrel = next(row for row in profiles if row.entity_id == "kestrel")
        self.assertEqual(kestrel.status, "qualified")
        self.assertGreaterEqual(kestrel.signal_count, 2)
        self.assertTrue(all(item["source_url"].startswith("https://") for item in kestrel.evidence))

    def test_source_kind_filter_is_enforced(self) -> None:
        config = load_config(HIRING / "config.json")
        evidence = extract_evidence(passages(HIRING / "corpus.json"), signals_from(config))
        self.assertTrue(all(item.source_kind in {"careers", "culture", "jobs"} for item in evidence))

    def test_non_hiring_configuration_proves_portability(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = run_profile(
                BUYER / "config.json",
                BUYER / "corpus.json",
                Path(temp),
                operator_approved=True,
            )
            self.assertGreaterEqual(result["manifest"]["qualified"], 1)
            self.assertEqual(result["manifest"]["project"], "Governed Workflow Readiness")

    def test_query_returns_evidence_not_just_entity_names(self) -> None:
        config = load_config(HIRING / "config.json")
        evidence = extract_evidence(passages(HIRING / "corpus.json"), signals_from(config))
        results = query_evidence(evidence, "ownership and autonomy")
        self.assertTrue(results)
        self.assertIn("matched_text", results[0])
        self.assertIn("source_url", results[0])

    def test_pipeline_writes_reproducible_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            run_profile(
                HIRING / "config.json",
                HIRING / "corpus.json",
                output,
                operator_approved=True,
            )
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"source-plan.json", "evidence.json", "profiles.json", "run.json"},
            )


if __name__ == "__main__":
    unittest.main()
