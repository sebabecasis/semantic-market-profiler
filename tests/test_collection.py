import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from semantic_market_profiler.collect import collect
from semantic_market_profiler.providers import digest
from semantic_market_profiler.pipeline import run_profile

ROOT = Path(__file__).resolve().parents[1]


class CollectionTests(unittest.TestCase):
    def config(self):
        value = json.loads((ROOT / "examples/hiring-philosophy/config.json").read_text())
        value["collection"] = [{"entity_id": "example", "entity_name": "Example", "domain": "example.test",
            "source_url": "https://example.test/careers", "source_kind": "careers"}]
        return value

    def test_changed_plan_blocked_before_fetch(self):
        config = self.config()
        old = digest(config)
        config["research_question"] = "changed"
        fetch = Mock(side_effect=AssertionError())
        with self.assertRaises(PermissionError):
            collect(config, old, fetch=fetch)
        fetch.assert_not_called()

    def test_collection_keeps_exact_source_and_reports_failure(self):
        config = self.config()
        text = "We hire for ownership and learning."
        result = collect(config, digest(config), fetch=lambda url: {"text": text})
        self.assertEqual(text, result["passages"][0]["text"])
        self.assertEqual(config["collection"][0]["source_url"], result["passages"][0]["source_url"])
        failed = collect(config, digest(config), fetch=Mock(side_effect=TimeoutError()))
        self.assertEqual(0, failed["sources_succeeded"])
        self.assertEqual("TimeoutError", failed["failures"][0]["error"])

    def test_missing_evidence_remains_in_coverage_and_inputs_are_snapshotted(self):
        config = self.config()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.json").write_text(json.dumps(config))
            (root / "corpus.json").write_text("[]")
            result = run_profile(root / "config.json", root / "corpus.json", root / "out", operator_approved=True, approved_hash=digest(config))
            self.assertEqual("no_evidence", result["profiles"][0]["status"])
            self.assertEqual(1, result["manifest"]["coverage"]["no_evidence"])
            self.assertEqual(config, result["manifest"]["config_snapshot"])

    def test_unreviewed_source_rejected(self):
        config = self.config()
        passage = {**config["collection"][0], "source_url": "https://other.test", "text": "ownership"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.json").write_text(json.dumps(config))
            (root / "corpus.json").write_text(json.dumps([passage]))
            with self.assertRaises(ValueError):
                run_profile(root / "config.json", root / "corpus.json", root / "out", operator_approved=True)

    def test_production_encoder_requires_bound_approval(self):
        encoder = Mock(provider="openai")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                run_profile(ROOT / "examples/hiring-philosophy/config.json", ROOT / "examples/hiring-philosophy/corpus.json", Path(directory), operator_approved=True, encoder=encoder)
