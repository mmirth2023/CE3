from __future__ import annotations

from datetime import datetime

from .models import GlobalSystemState


class GlobalSystemStateHistory:
    """
    Provides chronological and temporal access to canonical
    CE³ global system states.

    This layer allows CE³ to reconstruct the generalized
    system configuration through time.

    It does not determine causality, propagation, materiality,
    regime transition, or future outcomes.
    """

    def __init__(
        self,
        states: list[GlobalSystemState] | None = None,
    ) -> None:
        self._states: list[GlobalSystemState] = []

        for state in states or []:
            self.add(state)

    def add(
        self,
        state: GlobalSystemState,
    ) -> GlobalSystemState:
        if any(
            existing.id == state.id
            for existing in self._states
        ):
            raise ValueError(
                f"Global system state already exists: "
                f"{state.id}"
            )

        self._states.append(state)

        return state

    def all(self) -> list[GlobalSystemState]:
        return sorted(
            self._states,
            key=lambda state: state.state_time,
        )

    def get(
        self,
        state_id: str,
    ) -> GlobalSystemState:
        for state in self._states:
            if state.id == state_id:
                return state

        raise KeyError(
            f"Global system state not found: {state_id}"
        )

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[GlobalSystemState]:
        return [
            state
            for state in self.all()
            if start <= state.state_time <= end
        ]

    def as_of(
        self,
        timestamp: datetime,
    ) -> list[GlobalSystemState]:
        return [
            state
            for state in self.all()
            if state.state_time <= timestamp
        ]

    def latest(
        self,
        timestamp: datetime | None = None,
    ) -> GlobalSystemState | None:
        states = self.as_of(timestamp) if timestamp else self.all()

        if not states:
            return None

        return states[-1]

    def __len__(self) -> int:
        return len(self._states)