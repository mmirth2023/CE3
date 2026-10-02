from __future__ import annotations

from .models import MaterialityAssessment, MaterialityLevel


class MaterialityEngine:
    """
    First-pass deterministic materiality evaluator.

    This engine assesses the structural significance of a state
    change. It does not determine causality, propagation, market
    impact, or future outcomes.
    """

    def assess(
        self,
        *,
        magnitude: float,
        structural_relevance: float,
        persistence: float,
        confidence: float,
    ) -> MaterialityAssessment:
        """
        Produce an explainable materiality assessment.

        The current implementation uses a simple weighted score.
        This is intentionally a baseline implementation that can
        later be replaced or extended without changing the model.
        """

        self._validate_score(magnitude, "magnitude")
        self._validate_score(
            structural_relevance,
            "structural_relevance",
        )
        self._validate_score(persistence, "persistence")
        self._validate_score(confidence, "confidence")

        score = (
            magnitude * 0.30
            + structural_relevance * 0.30
            + persistence * 0.20
            + confidence * 0.20
        )

        level = self._level(score)

        rationale = [
            f"magnitude={magnitude:.2f}",
            f"structural_relevance={structural_relevance:.2f}",
            f"persistence={persistence:.2f}",
            f"confidence={confidence:.2f}",
            f"composite_score={score:.2f}",
        ]

        return MaterialityAssessment(
            level=level,
            magnitude=magnitude,
            structural_relevance=structural_relevance,
            persistence=persistence,
            confidence=confidence,
            rationale=rationale,
        )

    @staticmethod
    def _level(score: float) -> MaterialityLevel:
        if score < 0.20:
            return MaterialityLevel.NONE

        if score < 0.40:
            return MaterialityLevel.LOW

        if score < 0.60:
            return MaterialityLevel.MEDIUM

        if score < 0.80:
            return MaterialityLevel.HIGH

        return MaterialityLevel.CRITICAL

    @staticmethod
    def _validate_score(
        value: float,
        name: str,
    ) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{name} must be between 0.0 and 1.0"
            )