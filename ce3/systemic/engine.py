from __future__ import annotations

from datetime import datetime

from ce3.change.models import StateChangeAssessment

from .models import (
    SystemicChangeAssessment,
    SystemicLevel,
)


class SystemicChangeEngine:
    """
    Assesses whether a material state change has sufficient
    structural breadth or cross-system relevance to be
    considered systemic.

    This is a transparent baseline implementation.

    It does not determine propagation, causality, regime
    transition, economic impact, or future outcomes.
    """

    def assess(
        self,
        *,
        change_id: str,
        state_change: StateChangeAssessment,
        assessed_at: datetime,
        scope: float,
        dependency_relevance: float,
        cross_domain_relevance: float,
        persistence: float,
        confidence: float,
    ) -> SystemicChangeAssessment:
        """
        Assess the systemic significance of an existing
        state change.
        """

        values = {
            "scope": scope,
            "dependency_relevance": dependency_relevance,
            "cross_domain_relevance": cross_domain_relevance,
            "persistence": persistence,
            "confidence": confidence,
        }

        for name, value in values.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1"
                )

        composite = (
            scope * 0.25
            + dependency_relevance * 0.25
            + cross_domain_relevance * 0.25
            + persistence * 0.15
            + confidence * 0.10
        )

        if composite < 0.30:
            level = SystemicLevel.NONE
        elif composite < 0.60:
            level = SystemicLevel.LOCAL
        else:
            level = SystemicLevel.SYSTEMIC

        rationale = [
            f"scope={scope:.2f}",
            (
                "dependency_relevance="
                f"{dependency_relevance:.2f}"
            ),
            (
                "cross_domain_relevance="
                f"{cross_domain_relevance:.2f}"
            ),
            f"persistence={persistence:.2f}",
            f"confidence={confidence:.2f}",
            f"composite={composite:.2f}",
        ]

        return SystemicChangeAssessment(
            id=change_id,
            assessed_at=assessed_at,
            state_change=state_change,
            level=level,
            scope=scope,
            dependency_relevance=dependency_relevance,
            cross_domain_relevance=cross_domain_relevance,
            persistence=persistence,
            confidence=confidence,
            rationale=rationale,
        )