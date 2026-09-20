from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_config, signals_from
from .engine import build_profiles, extract_evidence
from .models import Passage
from .planner import make_source_plan


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_plan(config_path: Path, output_dir: Path) -> dict[str, Any]:
    config = load_config(config_path)
    plan = make_source_plan(config)
    write_json(output_dir / "source-plan.json", plan)
    return plan


def run_profile(
    config_path: Path,
    corpus_path: Path,
    output_dir: Path,
    *,
    operator_approved: bool = False,
) -> dict[str, Any]:
    if not operator_approved:
        raise PermissionError("Operator approval is required; rerun with --approve-plan")
    config = load_config(config_path)
    raw_passages = json.loads(corpus_path.read_text(encoding="utf-8"))
    passages = [Passage.from_dict(row) for row in raw_passages]
    plan = make_source_plan(config, approved=True)
    evidence = extract_evidence(passages, signals_from(config))
    profiles = build_profiles(evidence, config["qualification"])

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "source-plan.json", plan)
    write_json(output_dir / "evidence.json", [item.to_dict() for item in evidence])
    write_json(output_dir / "profiles.json", [item.to_dict() for item in profiles])
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": config["name"],
        "research_question": config["research_question"],
        "encoder": "ConceptHashEncoder",
        "passages": len(passages),
        "signals": len(config["signals"]),
        "evidence_matches": len(evidence),
        "profiles": len(profiles),
        "qualified": sum(profile.status == "qualified" for profile in profiles),
        "outputs": ["source-plan.json", "evidence.json", "profiles.json", "run.json"],
    }
    write_json(output_dir / "run.json", manifest)
    return {"manifest": manifest, "profiles": [item.to_dict() for item in profiles]}
