from __future__ import annotations

from datetime import datetime
from typing import Any

from .diff import StateSpaceDiff
from .models import StateSpaceDimension, StateSpacePosition
from .transition import (
    StateSpaceTransition,
    StateSpaceTransitionType,
)


class StateSpaceTransitionEngine:
    """
    Classify observed movement between two state-space positions.

    The engine is deterministic and descriptive. It does not
    forecast future states, infer causality, or determine whether
    a transition will continue.
    """

    def assess(
        self,
        *,
        transition_id: str,
        previous: StateSpacePosition,
        current: StateSpacePosition,
        assessed_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StateSpaceTransition:
        """
        Assess the observed transition between two positions.
        """
        diff = StateSpaceDiff.between(
            previous,
            current,
        )

        changed_dimensions = (
            diff.changed_dimension_names
        )

        transition_type = self._classify(
            previous=previous,
            current=current,
            diff=diff,
        )

        magnitude = self._calculate_magnitude(
            diff
        )

        confidence = min(
            previous.confidence,
            current.confidence,
        )

        rationale = self._build_rationale(
            previous=previous,
            current=current,
            diff=diff,
            transition_type=transition_type,
        )

        return StateSpaceTransition(
            id=transition_id,
            assessed_at=(
                assessed_at
                if assessed_at is not None
                else current.state_time
            ),
            previous_position_id=previous.id,
            current_position_id=current.id,
            previous_state_time=previous.state_time,
            current_state_time=current.state_time,
            transition_type=transition_type,
            changed_dimensions=changed_dimensions,
            magnitude=magnitude,
            confidence=confidence,
            state_space_diff=diff,
            rationale=rationale,
            source_event_ids=list(
                dict.fromkeys(
                    previous.source_event_ids
                    + current.source_event_ids
                )
            ),
            source_observation_ids=list(
                dict.fromkeys(
                    previous.source_observation_ids
                    + current.source_observation_ids
                )
            ),
            metadata=dict(metadata or {}),
        )

    def _classify(
        self,
        *,
        previous: StateSpacePosition,
        current: StateSpacePosition,
        diff: StateSpaceDiff,
    ) -> StateSpaceTransitionType:
        """
        Classify the observed transition.

        Classification is based only on observed dimensional
        movement and structural additions/removals.
        """
        if not diff.has_changes:
            return StateSpaceTransitionType.NONE

        increases = 0
        decreases = 0

        for previous_value, current_value in (
            diff.changed_dimensions.values()
        ):
            if (
                previous_value is not None
                and current_value is not None
            ):
                if current_value > previous_value:
                    increases += 1
                elif current_value < previous_value:
                    decreases += 1

        structural_change = bool(
            diff.added_constraints
            or diff.removed_constraints
            or diff.added_dependencies
            or diff.removed_dependencies
            or diff.added_shocks
            or diff.removed_shocks
            or diff.added_propagation_path_ids
            or diff.removed_propagation_path_ids
        )

        if structural_change:
            return StateSpaceTransitionType.STRUCTURAL_SHIFT

        if increases > 0 and decreases > 0:
            return StateSpaceTransitionType.DIMENSIONAL_SHIFT

        if decreases > 0:
            return StateSpaceTransitionType.DETERIORATION

        if increases > 0:
            return StateSpaceTransitionType.RECOVERY

        if (
            diff.added_labels
            or diff.removed_labels
            or diff.metadata_changes
        ):
            return StateSpaceTransitionType.NORMALIZATION

        return StateSpaceTransitionType.UNKNOWN

    @staticmethod
    def _calculate_magnitude(
        diff: StateSpaceDiff,
    ) -> float:
        """
        Calculate normalized observed dimensional movement.

        Magnitude is the mean absolute change across dimensions
        that changed in both positions.
        """
        changes: list[float] = []

        for previous_value, current_value in (
            diff.changed_dimensions.values()
        ):
            if (
                previous_value is not None
                and current_value is not None
            ):
                changes.append(
                    abs(
                        current_value
                        - previous_value
                    )
                )

        if not changes:
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                sum(changes) / len(changes),
            ),
        )

    @staticmethod
    def _build_rationale(
        *,
        previous: StateSpacePosition,
        current: StateSpacePosition,
        diff: StateSpaceDiff,
        transition_type: StateSpaceTransitionType,
    ) -> list[str]:
        """
        Produce concise deterministic explanations for the
        observed classification.
        """
        rationale: list[str] = []

        if diff.changed_dimensions:
            names = [
                dimension.value
                for dimension in diff.changed_dimensions
            ]

            rationale.append(
                "Changed dimensions: "
                + ", ".join(sorted(names))
                + "."
            )

        if diff.added_constraints:
            rationale.append(
                "Constraints added: "
                + ", ".join(
                    sorted(diff.added_constraints)
                )
                + "."
            )

        if diff.removed_constraints:
            rationale.append(
                "Constraints removed: "
                + ", ".join(
                    sorted(diff.removed_constraints)
                )
                + "."
            )

        if diff.added_dependencies:
            rationale.append(
                "Dependencies added: "
                + ", ".join(
                    sorted(diff.added_dependencies)
                )
                + "."
            )

        if diff.removed_dependencies:
            rationale.append(
                "Dependencies removed: "
                + ", ".join(
                    sorted(diff.removed_dependencies)
                )
                + "."
            )

        if diff.added_shocks:
            rationale.append(
                "Active shocks added: "
                + ", ".join(
                    sorted(diff.added_shocks)
                )
                + "."
            )

        if diff.removed_shocks:
            rationale.append(
                "Active shocks removed: "
                + ", ".join(
                    sorted(diff.removed_shocks)
                )
                + "."
            )

        if transition_type == (
            StateSpaceTransitionType.NONE
        ):
            rationale.append(
                "No observable state-space change detected."
            )

        return rationale