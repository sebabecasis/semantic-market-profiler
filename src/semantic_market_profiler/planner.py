from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from .config import signals_from, sources_from
from .providers import digest


def make_source_plan(config: dict[str, Any], *, approved: bool = False) -> dict[str, Any]:
    return {
        "project": config["name"],
        "config_hash": digest(config),
        "research_question": config["research_question"],
        "status": "approved" if approved else "pending_operator_review",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "operator_controls": [
            "Edit source locators and rationales before collection.",
            "Edit signal queries, source filters and thresholds before profiling.",
            "Approve the plan explicitly before a run.",
            "Inspect exact evidence before accepting a qualification.",
        ],
        "sources": [asdict(source) for source in sources_from(config)],
        "signals": [asdict(signal) for signal in signals_from(config)],
        "qualification": config["qualification"],
    }
