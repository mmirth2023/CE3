from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .models import StateSpaceDimension, StateSpacePosition


class StateSpaceDiff(BaseModel):
    """
    Descriptive difference between two state-space positions.

    The diff records observable structural changes between two
    positions. It does not infer causality, predict future states,
    or determine whether a transition will occur.
    """

    previous_position_id: str
    current_position_id: str

    previous_state_time: datetime
    current_state_time: datetime

    changed_dimensions: dict[
        StateSpaceDimension,
        tuple[float | None, float | None],
    ] = Field(
        default_factory=dict,
    )

    added_labels: list[str] = Field(
        default_factory=list,
    )

    removed_labels: list[str] = Field(
        default_factory=list,
    )

    added_constraints: list[str] = Field(
        default_factory=list,
    )

    removed_constraints: list[str] = Field(
        default_factory=list,
    )

    added_dependencies: list[str] = Field(
        default_factory=list,
    )

    removed_dependencies: list[str] = Field(
        default_factory=list,
    )

    added_shocks: list[str] = Field(
        default_factory=list,
    )

    removed_shocks: list[str] = Field(
        default_factory=list,
    )

    added_propagation_path_ids: list[str] = Field(
        default_factory=list,
    )

    removed_propagation_path_ids: list[str] = Field(
        default_factory=list,
    )

    added_source_event_ids: list[str] = Field(
        default_factory=list,
    )

    removed_source_event_ids: list[str] = Field(
        default_factory=list,
    )

    added_source_observation_ids: list[str] = Field(
        default_factory=list,
    )

    removed_source_observation_ids: list[str] = Field(
        default_factory=list,
    )

    confidence_change: tuple[float, float] | None = None
    uncertainty_change: tuple[float, float] | None = None

    metadata_changes: dict[
        str,
        tuple[Any, Any],
    ] = Field(
        default_factory=dict,
    )

    @property
    def has_changes(self) -> bool:
        """
        Return whether any observable state-space change exists.
        """
        return any(
            [
                bool(self.changed_dimensions),
                bool(self.added_labels),
                bool(self.removed_labels),
                bool(self.added_constraints),
                bool(self.removed_constraints),
                bool(self.added_dependencies),
                bool(self.removed_dependencies),
                bool(self.added_shocks),
                bool(self.removed_shocks),
                bool(self.added_propagation_path_ids),
                bool(self.removed_propagation_path_ids),
                bool(self.added_source_event_ids),
                bool(self.removed_source_event_ids),
                bool(self.added_source_observation_ids),
                bool(self.removed_source_observation_ids),
                self.confidence_change is not None,
                self.uncertainty_change is not None,
                bool(self.metadata_changes),
            ]
        )

    @property
    def changed_dimension_names(self) -> list[str]:
        """
        Return changed state-space dimensions as string values.
        """
        return [
            dimension.value
            for dimension in self.changed_dimensions
        ]

    @classmethod
    def between(
        cls,
        previous: StateSpacePosition,
        current: StateSpacePosition,
    ) -> StateSpaceDiff:
        """
        Construct a descriptive diff between two positions.
        """
        dimensions: dict[
            StateSpaceDimension,
            tuple[float | None, float | None],
        ] = {}

        all_dimensions = set(previous.dimensions) | set(
            current.dimensions
        )

        for dimension in all_dimensions:
            previous_value = previous.dimensions.get(dimension)
            current_value = current.dimensions.get(dimension)

            if previous_value != current_value:
                dimensions[dimension] = (
                    previous_value,
                    current_value,
                )

        metadata_changes: dict[
            str,
            tuple[Any, Any],
        ] = {}

        all_metadata_keys = (
            set(previous.metadata)
            | set(current.metadata)
        )

        for key in all_metadata_keys:
            previous_value = previous.metadata.get(key)
            current_value = current.metadata.get(key)

            if previous_value != current_value:
                metadata_changes[key] = (
                    previous_value,
                    current_value,
                )

        return cls(
            previous_position_id=previous.id,
            current_position_id=current.id,
            previous_state_time=previous.state_time,
            current_state_time=current.state_time,
            changed_dimensions=dimensions,
            added_labels=sorted(
                set(current.labels) - set(previous.labels)
            ),
            removed_labels=sorted(
                set(previous.labels) - set(current.labels)
            ),
            added_constraints=sorted(
                set(current.active_constraints)
                - set(previous.active_constraints)
            ),
            removed_constraints=sorted(
                set(previous.active_constraints)
                - set(current.active_constraints)
            ),
            added_dependencies=sorted(
                set(current.active_dependencies)
                - set(previous.active_dependencies)
            ),
            removed_dependencies=sorted(
                set(previous.active_dependencies)
                - set(current.active_dependencies)
            ),
            added_shocks=sorted(
                set(current.active_shocks)
                - set(previous.active_shocks)
            ),
            removed_shocks=sorted(
                set(previous.active_shocks)
                - set(current.active_shocks)
            ),
            added_propagation_path_ids=sorted(
                set(current.propagation_path_ids)
                - set(previous.propagation_path_ids)
            ),
            removed_propagation_path_ids=sorted(
                set(previous.propagation_path_ids)
                - set(current.propagation_path_ids)
            ),
            added_source_event_ids=sorted(
                set(current.source_event_ids)
                - set(previous.source_event_ids)
            ),
            removed_source_event_ids=sorted(
                set(previous.source_event_ids)
                - set(current.source_event_ids)
            ),
            added_source_observation_ids=sorted(
                set(current.source_observation_ids)
                - set(previous.source_observation_ids)
            ),
            removed_source_observation_ids=sorted(
                set(previous.source_observation_ids)
                - set(current.source_observation_ids)
            ),
            confidence_change=(
                (previous.confidence, current.confidence)
                if previous.confidence != current.confidence
                else None
            ),
            uncertainty_change=(
                (previous.uncertainty, current.uncertainty)
                if previous.uncertainty != current.uncertainty
                else None
            ),
            metadata_changes=metadata_changes,
        )