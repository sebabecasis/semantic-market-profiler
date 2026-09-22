from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_config, signals_from
from .engine import build_profiles, extract_evidence
from .models import Passage, Profile
from .planner import make_source_plan
from .embedding import ConceptHashEncoder
from .providers import digest


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
    encoder=None,
    approved_hash: str | None = None,
) -> dict[str, Any]:
    if not operator_approved:
        raise PermissionError("Operator approval is required; rerun with --approve-plan")
    config = load_config(config_path)
    if approved_hash is not None and approved_hash != digest(config):
        raise PermissionError("Configuration differs from the reviewed plan")
    active = encoder or ConceptHashEncoder()
    if getattr(active, "provider", "demo") != "demo" and not approved_hash:
        raise PermissionError("Production runs require the reviewed config hash")
    raw_passages = json.loads(corpus_path.read_text(encoding="utf-8"))
    passages = [Passage.from_dict(row) for row in raw_passages]
    plan = make_source_plan(config, approved=True)
    if config.get("collection"):
        allowed_sources = {(r["entity_id"], r["source_url"], r["source_kind"]) for r in config["collection"]}
        if any((p.entity_id, p.source_url, p.source_kind) not in allowed_sources for p in passages):
            raise ValueError("Corpus includes a source outside the reviewed collection plan")
    evidence = extract_evidence(passages, signals_from(config), encoder=active)
    profiles = build_profiles(evidence, config["qualification"])
    universe = {p.entity_id: {"entity_name": p.entity_name, "domain": p.domain} for p in passages}
    universe.update({r["entity_id"]: r for r in config.get("collection", [])})
    matched = {p.entity_id for p in profiles}
    for entity_id, row in universe.items():
        if entity_id not in matched:
            profiles.append(Profile(entity_id, row["entity_name"], row["domain"], "no_evidence", [], 0, 0.0,
                                    ["No matching evidence; this is not a negative qualification"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "source-plan.json", plan)
    write_json(output_dir / "evidence.json", [item.to_dict() for item in evidence])
    write_json(output_dir / "profiles.json", [item.to_dict() for item in profiles])
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": config["name"],
        "research_question": config["research_question"],
        "encoder": type(active).__name__,
        "embedding": {"provider": getattr(active, "provider", "demo"), "model": getattr(active, "model", None), "dimensions": active.dimensions},
        "config_hash": digest(config),
        "corpus_hash": digest(raw_passages),
        "config_snapshot": config,
        "corpus_snapshot": raw_passages,
        "coverage": {"entities": len(universe), "with_evidence": len(matched), "no_evidence": len(universe) - len(matched)},
        "passages": len(passages),
        "signals": len(config["signals"]),
        "evidence_matches": len(evidence),
        "profiles": len(profiles),
        "qualified": sum(profile.status == "qualified" for profile in profiles),
        "outputs": ["source-plan.json", "evidence.json", "profiles.json", "run.json"],
    }
    write_json(output_dir / "run.json", manifest)
    return {"manifest": manifest, "profiles": [item.to_dict() for item in profiles]}
