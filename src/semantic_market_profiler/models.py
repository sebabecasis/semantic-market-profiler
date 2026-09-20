from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Source:
    kind: str
    locator: str
    rationale: str


@dataclass(frozen=True)
class Signal:
    id: str
    name: str
    query: str
    source_kinds: tuple[str, ...] = ()
    threshold: float = 0.2


@dataclass(frozen=True)
class Passage:
    entity_id: str
    entity_name: str
    domain: str
    source_url: str
    source_kind: str
    text: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Passage":
        return cls(**value)


@dataclass(frozen=True)
class Evidence:
    entity_id: str
    entity_name: str
    domain: str
    signal_id: str
    signal_name: str
    score: float
    text: str
    source_url: str
    source_kind: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Profile:
    entity_id: str
    entity_name: str
    domain: str
    status: str
    matched_signals: list[str]
    signal_count: int
    average_score: float
    qualification_reasons: list[str]
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
