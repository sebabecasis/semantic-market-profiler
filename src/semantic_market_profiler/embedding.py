from __future__ import annotations

import hashlib
import math
import re
from collections import Counter


TOKEN = re.compile(r"[a-z0-9]+")


class ConceptHashEncoder:
    """Deterministic demo encoder behind a replaceable provider boundary."""

    ALIASES = {
        "accountability": "ownership",
        "autonomous": "ownership",
        "autonomy": "ownership",
        "owners": "ownership",
        "learn": "learning",
        "learners": "learning",
        "curious": "learning",
        "adapt": "learning",
        "adapting": "learning",
        "distributed": "remote",
        "global": "remote",
        "manual": "repetitive",
        "spreadsheet": "repetitive",
        "spreadsheets": "repetitive",
        "approvals": "approval",
        "audit": "governance",
        "auditable": "governance",
        "compliance": "governance",
        "workflows": "workflow",
        "processes": "workflow",
        "operations": "ops",
        "operational": "ops",
    }
    STOP = {"a", "an", "and", "are", "for", "from", "in", "of", "on", "the", "to", "we", "with"}

    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def concepts(self, text: str) -> list[str]:
        return [
            self.ALIASES.get(token, token)
            for token in TOKEN.findall(text.casefold())
            if token not in self.STOP
        ]

    def encode(self, text: str) -> list[float]:
        concepts = self.concepts(text)
        features = concepts + [f"{a}:{b}" for a, b in zip(concepts, concepts[1:])]
        vector = [0.0] * self.dimensions
        for feature, count in Counter(features).items():
            digest = hashlib.sha256(feature.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign * count
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Vectors must have equal dimensions")
    return sum(a * b for a, b in zip(left, right))
