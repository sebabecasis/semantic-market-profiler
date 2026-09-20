from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Signal, Source


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = ["name", "research_question", "sources", "signals", "qualification"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Config missing fields: {', '.join(missing)}")
    if not config["sources"] or not config["signals"]:
        raise ValueError("Config requires at least one source and one signal")
    signal_ids = [row["id"] for row in config["signals"]]
    if len(signal_ids) != len(set(signal_ids)):
        raise ValueError("Signal ids must be unique")
    return config


def sources_from(config: dict[str, Any]) -> list[Source]:
    return [Source(**row) for row in config["sources"]]


def signals_from(config: dict[str, Any]) -> list[Signal]:
    return [
        Signal(
            id=row["id"],
            name=row["name"],
            query=row["query"],
            source_kinds=tuple(row.get("source_kinds", [])),
            threshold=float(row.get("threshold", 0.2)),
        )
        for row in config["signals"]
    ]
