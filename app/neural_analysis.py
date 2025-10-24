from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass
class AnalysisResult:
    decisions: list[str]
    assignments: list[tuple[str | None, str, datetime | None]]
    corrections: list[str]


class MockNeuralAnalyzer:
    """Simplified neural network placeholder.

    The goal of this class is to imitate the behaviour of an NLP-powered
    classifier. In a production environment it can be replaced with a real
    model served through an API. The current implementation extracts
    decisions, action items and corrections from the text based on common
    Russian meeting protocol markers.
    """

    decision_patterns: tuple[str, ...] = (
        r"решено[:\-]?\s*(?P<text>.+)",
        r"принято\s+решение[:\-]?\s*(?P<text>.+)",
    )
    assignment_patterns: tuple[str, ...] = (
        r"поручить[:\-]?\s*(?P<responsible>[А-ЯЁA-Z][^:,.]*)[,\s]+(?P<text>.+?)"
        r"(?:\s+срок[:\-]?\s*(?P<due>[^.]+))?",
        r"(?P<responsible>[А-ЯЁA-Z][^:,.]*)\s+должен[:\-]?\s*(?P<text>.+?)"
        r"(?:\s+до\s*(?P<due>[^.]+))?",
    )
    correction_patterns: tuple[str, ...] = (
        r"исправить[:\-]?\s*(?P<text>.+)",
        r"ошибка[:\-]?\s*(?P<text>.+)",
    )

    def analyze(self, text: str) -> AnalysisResult:
        sentences = split_text(text)
        decisions = [match.group("text").strip() for match in self._find(sentences, self.decision_patterns)]
        assignments = [
            (
                (match.group("responsible").strip() if match.group("responsible") else None),
                match.group("text").strip(),
                parse_due(match.group("due")) if match.groupdict().get("due") else None,
            )
            for match in self._find(sentences, self.assignment_patterns)
        ]
        corrections = [match.group("text").strip() for match in self._find(sentences, self.correction_patterns)]
        return AnalysisResult(decisions, assignments, corrections)

    def _find(self, sentences: Iterable[str], patterns: Iterable[str]):
        for sentence in sentences:
            for pattern in patterns:
                if match := re.search(pattern, sentence, re.IGNORECASE):
                    yield match


def split_text(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text)
    return re.split(r"(?<=[.!?])\s+", cleaned)


def parse_due(raw_due: str | None) -> datetime | None:
    if not raw_due:
        return None
    raw_due = raw_due.strip()
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw_due, fmt)
        except ValueError:
            continue
    return None
