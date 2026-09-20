from __future__ import annotations

from collections import defaultdict
from typing import Any

from .embedding import ConceptHashEncoder, cosine
from .models import Evidence, Passage, Profile, Signal


def extract_evidence(
    passages: list[Passage],
    signals: list[Signal],
    *,
    encoder: ConceptHashEncoder | None = None,
) -> list[Evidence]:
    active = encoder or ConceptHashEncoder()
    vectors = [(passage, active.encode(passage.text)) for passage in passages]
    output: list[Evidence] = []

    for signal in signals:
        query_vector = active.encode(signal.query)
        allowed = set(signal.source_kinds)
        best: dict[str, tuple[float, Passage]] = {}
        for passage, vector in vectors:
            if allowed and passage.source_kind not in allowed:
                continue
            score = cosine(query_vector, vector)
            if score < signal.threshold:
                continue
            previous = best.get(passage.entity_id)
            if previous is None or score > previous[0]:
                best[passage.entity_id] = (score, passage)
        for entity_id, (score, passage) in sorted(best.items(), key=lambda row: (-row[1][0], row[0])):
            output.append(
                Evidence(
                    entity_id=entity_id,
                    entity_name=passage.entity_name,
                    domain=passage.domain,
                    signal_id=signal.id,
                    signal_name=signal.name,
                    score=score,
                    text=passage.text,
                    source_url=passage.source_url,
                    source_kind=passage.source_kind,
                )
            )
    return output


def build_profiles(evidence: list[Evidence], rules: dict[str, Any]) -> list[Profile]:
    grouped: dict[str, list[Evidence]] = defaultdict(list)
    for item in evidence:
        grouped[item.entity_id].append(item)

    minimum_signals = int(rules.get("minimum_signals", 1))
    minimum_average = float(rules.get("minimum_average_score", 0.0))
    require_any = set(rules.get("require_any", []))
    profiles: list[Profile] = []

    for entity_id, items in grouped.items():
        ordered = sorted(items, key=lambda item: (-item.score, item.signal_id))
        matched = {item.signal_id for item in ordered}
        average = sum(item.score for item in ordered) / len(ordered)
        reasons = [f"matched {len(matched)} distinct signals"]
        gates = [len(matched) >= minimum_signals, average >= minimum_average]
        if require_any:
            required_match = sorted(matched & require_any)
            gates.append(bool(required_match))
            reasons.append(
                "required signal matched: " + ", ".join(required_match)
                if required_match
                else "no required signal matched"
            )
        status = "qualified" if all(gates) else "review"
        profiles.append(
            Profile(
                entity_id=entity_id,
                entity_name=ordered[0].entity_name,
                domain=ordered[0].domain,
                status=status,
                matched_signals=sorted(matched),
                signal_count=len(matched),
                average_score=average,
                qualification_reasons=reasons,
                evidence=[item.to_dict() for item in ordered],
            )
        )
    profiles.sort(
        key=lambda row: (
            row.status != "qualified",
            -row.signal_count,
            -row.average_score,
            row.entity_name.casefold(),
        )
    )
    return profiles


def query_evidence(
    evidence: list[Evidence], query: str, *, top: int = 5, encoder: ConceptHashEncoder | None = None
) -> list[dict[str, Any]]:
    active = encoder or ConceptHashEncoder()
    query_vector = active.encode(query)
    best: dict[str, tuple[float, Evidence]] = {}
    for item in evidence:
        score = cosine(query_vector, active.encode(item.text))
        previous = best.get(item.entity_id)
        if previous is None or score > previous[0]:
            best[item.entity_id] = (score, item)
    rows = [
        {
            "entity_id": item.entity_id,
            "entity_name": item.entity_name,
            "domain": item.domain,
            "score": score,
            "matched_text": item.text,
            "source_url": item.source_url,
        }
        for score, item in best.values()
    ]
    rows.sort(key=lambda row: (-row["score"], row["entity_name"].casefold()))
    return rows[:top]
