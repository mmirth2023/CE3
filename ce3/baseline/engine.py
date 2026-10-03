from __future__ import annotations

from datetime import datetime
from typing import Any

from .models import BaselineReference


class BaselineEngine:
    """
    Constructs canonical baseline references from explicitly supplied
    historical, structural, conditional, and comparable-state evidence.

    The engine constructs a reference representation only.

    It does not:
    - calculate baseline deviation,
    - determine causality,
    - assess materiality,
    - infer propagation,
    - identify regime transitions,
    - predict future outcomes.
    """

    def build(
        self,
        *,
        baseline_id: str,
        system_id: str,
        dimension: str,
        established_at: datetime,
        reference_state: dict[str, Any] | None = None,
        reference_observation_ids: list[str] | None = None,
        comparable_state_ids: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
        stability: float = 1.0,
        confidence: float = 1.0,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaselineReference:
        """
        Construct a baseline reference from explicitly supplied inputs.
        """
        return BaselineReference(
            id=baseline_id,
            system_id=system_id,
            dimension=dimension,
            established_at=established_at,
            valid_from=valid_from,
            valid_to=valid_to,
            reference_state=reference_state or {},
            reference_observation_ids=reference_observation_ids or [],
            comparable_state_ids=comparable_state_ids or [],
            conditions=conditions or {},
            stability=stability,
            confidence=confidence,
            metadata=metadata or {},
        )

    def build_from_historical_state(
        self,
        *,
        baseline_id: str,
        system_id: str,
        dimension: str,
        established_at: datetime,
        historical_state: dict[str, Any],
        observation_ids: list[str] | None = None,
        comparable_state_ids: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
        stability: float = 1.0,
        confidence: float = 1.0,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaselineReference:
        """
        Construct a baseline directly from an explicitly selected
        historical state.
        """
        return self.build(
            baseline_id=baseline_id,
            system_id=system_id,
            dimension=dimension,
            established_at=established_at,
            reference_state=historical_state,
            reference_observation_ids=observation_ids,
            comparable_state_ids=comparable_state_ids,
            conditions=conditions,
            stability=stability,
            confidence=confidence,
            valid_from=valid_from,
            valid_to=valid_to,
            metadata=metadata,
        )

    def build_from_comparable_states(
        self,
        *,
        baseline_id: str,
        system_id: str,
        dimension: str,
        established_at: datetime,
        reference_state: dict[str, Any],
        comparable_state_ids: list[str],
        conditions: dict[str, Any] | None = None,
        stability: float = 1.0,
        confidence: float = 1.0,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaselineReference:
        """
        Construct a baseline from an explicitly selected set of
        historically comparable states.

        The supplied reference_state is treated as the canonical
        representation produced by the caller's comparison process.
        This method does not perform statistical inference itself.
        """
        return self.build(
            baseline_id=baseline_id,
            system_id=system_id,
            dimension=dimension,
            established_at=established_at,
            reference_state=reference_state,
            comparable_state_ids=comparable_state_ids,
            conditions=conditions,
            stability=stability,
            confidence=confidence,
            valid_from=valid_from,
            valid_to=valid_to,
            metadata=metadata,
        )