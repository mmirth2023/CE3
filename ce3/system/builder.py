from __future__ import annotations

from datetime import datetime
from typing import Any

from .models import GlobalSystemState


class GlobalSystemStateBuilder:
    """
    Assembles a canonical GlobalSystemState from explicitly
    supplied CE³ state components.

    This layer is an assembly mechanism.

    It does not infer causality, propagation, materiality,
    systemic impact, regime transitions, economic consequences,
    or future outcomes.
    """

    def build(
        self,
        *,
        state_id: str,
        state_time: datetime,
        entities: dict[str, Any] | None = None,
        relationships: dict[str, Any] | None = None,
        physical: dict[str, Any] | None = None,
        economic: dict[str, Any] | None = None,
        financial: dict[str, Any] | None = None,
        political: dict[str, Any] | None = None,
        information: dict[str, Any] | None = None,
        infrastructure: dict[str, Any] | None = None,
        market: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
        dependencies: dict[str, Any] | None = None,
        active_shocks: dict[str, Any] | None = None,
        observability: dict[str, Any] | None = None,
        adaptations: dict[str, Any] | None = None,
        propagation_paths: dict[str, Any] | None = None,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        confidence: float = 1.0,
        uncertainty: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GlobalSystemState:
        return GlobalSystemState(
            id=state_id,
            state_time=state_time,
            entities=entities or {},
            relationships=relationships or {},
            physical=physical or {},
            economic=economic or {},
            financial=financial or {},
            political=political or {},
            information=information or {},
            infrastructure=infrastructure or {},
            market=market or {},
            constraints=constraints or {},
            dependencies=dependencies or {},
            active_shocks=active_shocks or {},
            observability=observability or {},
            adaptations=adaptations or {},
            propagation_paths=propagation_paths or {},
            source_event_ids=source_event_ids or [],
            source_observation_ids=source_observation_ids or [],
            confidence=confidence,
            uncertainty=uncertainty or {},
            metadata=metadata or {},
        )