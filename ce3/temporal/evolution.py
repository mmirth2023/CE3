from __future__ import annotations

from pydantic import BaseModel, Field

from .state_diff import StateDiff
from .state_history import StateHistory


class StateEvolution(BaseModel):
    """
    Chronological evolution of CE³ state.

    Each StateDiff represents the structural change between two
    consecutive canonical state versions.

    This layer describes evolution only. It does not determine
    materiality, causality, propagation, or economic significance.
    """

    state_diffs: list[StateDiff] = Field(
        default_factory=list,
    )

    @property
    def changed(self) -> bool:
        """
        Whether any state change occurred across the evolution.
        """

        return any(diff.changed for diff in self.state_diffs)

    @property
    def change_count(self) -> int:
        """
        Number of state-version transitions represented.
        """

        return len(self.state_diffs)

    @classmethod
    def from_history(
        cls,
        history: StateHistory,
    ) -> StateEvolution:
        """
        Build chronological state evolution from StateHistory.
        """

        versions = history.all()

        if len(versions) < 2:
            return cls()

        diffs = [
            StateDiff.between(previous, current)
            for previous, current in zip(
                versions,
                versions[1:],
            )
        ]

        return cls(state_diffs=diffs)