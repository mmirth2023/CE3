from __future__ import annotations

from datetime import datetime
from typing import Any

from ce3.system.models import GlobalSystemState

from .models import StateSpaceDimension, StateSpacePosition


class StateSpaceEngine:
    """
    Construct a state-space position from the canonical global
    system state.

    The engine performs deterministic representation and
    normalization only. It does not predict future states,
    infer causality, or determine whether a transition will occur.
    """

    def build(
        self,
        *,
        position_id: str,
        system_state: GlobalSystemState,
        state_time: datetime | None = None,
        labels: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StateSpacePosition:
        """
        Build a state-space position from a global system state.
        """
        dimensions = self._build_dimensions(system_state)

        return StateSpacePosition(
            id=position_id,
            state_time=(
                state_time
                if state_time is not None
                else system_state.state_time
            ),
            dimensions=dimensions,
            labels=list(labels or []),
            active_constraints=list(
                system_state.constraints.keys()
            ),
            active_dependencies=list(
                system_state.dependencies.keys()
            ),
            active_shocks=list(
                system_state.active_shocks.keys()
            ),
            propagation_path_ids=list(
                system_state.propagation_paths.keys()
            ),
            source_event_ids=list(
                system_state.source_event_ids
            ),
            source_observation_ids=list(
                system_state.source_observation_ids
            ),
            confidence=system_state.confidence,
            uncertainty=self._uncertainty_score(
                system_state.uncertainty
            ),
            metadata=dict(metadata or {}),
        )

    def _build_dimensions(
        self,
        system_state: GlobalSystemState,
    ) -> dict[StateSpaceDimension, float]:
        """
        Construct normalized state-space dimensions.

        These values represent observable presence in the
        corresponding system-state domains. They are not forecasts
        or assessments of future outcomes.
        """
        return {
            StateSpaceDimension.PHYSICAL: self._presence_score(
                system_state.physical
            ),
            StateSpaceDimension.ECONOMIC: self._presence_score(
                system_state.economic
            ),
            StateSpaceDimension.FINANCIAL: self._presence_score(
                system_state.financial
            ),
            StateSpaceDimension.POLITICAL: self._presence_score(
                system_state.political
            ),
            StateSpaceDimension.INFORMATION: self._presence_score(
                system_state.information
            ),
            StateSpaceDimension.INFRASTRUCTURE: self._presence_score(
                system_state.infrastructure
            ),
            StateSpaceDimension.CONNECTIVITY: self._connectivity_score(
                system_state
            ),
            StateSpaceDimension.DEPENDENCY: self._collection_score(
                system_state.dependencies
            ),
            StateSpaceDimension.CONSTRAINT: self._collection_score(
                system_state.constraints
            ),
            StateSpaceDimension.RESILIENCE: self._adaptation_score(
                system_state
            ),
            StateSpaceDimension.ADAPTATION: self._adaptation_score(
                system_state
            ),
        }

    @staticmethod
    def _presence_score(
        value: dict[str, Any],
    ) -> float:
        """
        Represent whether a system-state domain contains
        observable information.

        Empty domains receive 0.0. Non-empty domains receive 1.0.
        """
        return 1.0 if value else 0.0

    @staticmethod
    def _collection_score(
        values: dict[str, Any],
    ) -> float:
        """
        Represent whether a structural collection contains
        observable elements.

        Empty collections receive 0.0. Non-empty collections
        receive 1.0.
        """
        return 1.0 if values else 0.0

    @staticmethod
    def _connectivity_score(
        system_state: GlobalSystemState,
    ) -> float:
        """
        Represent whether observable relationships connect
        entities in the current system state.
        """
        if not system_state.relationships:
            return 0.0

        return 1.0

    @staticmethod
    def _adaptation_score(
        system_state: GlobalSystemState,
    ) -> float:
        """
        Represent whether observable adaptations exist.

        This does not assess whether an adaptation is effective.
        """
        return 1.0 if system_state.adaptations else 0.0

    @staticmethod
    def _uncertainty_score(
        uncertainty: dict[str, Any],
    ) -> float:
        """
        Extract a normalized uncertainty value when the canonical
        uncertainty dictionary explicitly provides one.

        Supported scalar keys are checked deterministically.
        If no scalar uncertainty value is supplied, the presence
        of uncertainty information is represented as 1.0 and an
        empty dictionary as 0.0.
        """
        for key in (
            "score",
            "value",
            "level",
            "uncertainty",
        ):
            value = uncertainty.get(key)

            if isinstance(value, (int, float)):
                return max(
                    0.0,
                    min(1.0, float(value)),
                )

        return 1.0 if uncertainty else 0.0