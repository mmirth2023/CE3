from __future__ import annotations

from typing import Any

from ce3.temporal.state_diff import StateDiff
from ce3.temporal.state_version import StateVersion

from .models import GlobalSystemState


class GlobalSystemStateDiff:
    """
    Compares two GlobalSystemState snapshots using the canonical
    CE³ temporal state-diff mechanism.

    This layer adapts generalized system state to the existing
    domain-agnostic StateVersion and StateDiff representations.

    Only substantive system-state dimensions are compared.
    Snapshot identity, timestamps, lineage, confidence,
    uncertainty, and metadata are not themselves treated as
    structural system-state changes.

    It identifies structural differences only.

    It does not determine causality, materiality, systemic
    significance, propagation, regime transition, economic
    consequences, or future outcomes.
    """

    _STATE_DIMENSIONS = (
        "entities",
        "relationships",
        "physical",
        "economic",
        "financial",
        "political",
        "information",
        "infrastructure",
        "market",
        "constraints",
        "dependencies",
        "active_shocks",
        "observability",
        "adaptations",
        "propagation_paths",
    )

    @classmethod
    def between(
        cls,
        previous: GlobalSystemState,
        current: GlobalSystemState,
    ) -> StateDiff:
        previous_version = StateVersion(
            id=previous.id,
            state_time=previous.state_time,
            state=cls._state_payload(previous),
            source_event_ids=previous.source_event_ids,
            source_observation_ids=previous.source_observation_ids,
            confidence=previous.confidence,
            metadata=previous.metadata,
        )

        current_version = StateVersion(
            id=current.id,
            state_time=current.state_time,
            state=cls._state_payload(current),
            source_event_ids=current.source_event_ids,
            source_observation_ids=current.source_observation_ids,
            confidence=current.confidence,
            metadata=current.metadata,
        )

        return StateDiff.between(
            previous_version,
            current_version,
        )

    @classmethod
    def _state_payload(
        cls,
        state: GlobalSystemState,
    ) -> dict[str, Any]:
        payload = state.model_dump()

        return {
            dimension: payload[dimension]
            for dimension in cls._STATE_DIMENSIONS
        }