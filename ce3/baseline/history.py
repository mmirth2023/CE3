from __future__ import annotations

from datetime import datetime

from .models import BaselineReference


class BaselineHistory:
    """
    Temporal history of canonical baseline references.

    BaselineHistory stores baseline references in chronological order
    and provides deterministic temporal queries.

    It does not calculate deviations, infer causality, assess materiality,
    or determine future outcomes.
    """

    def __init__(self) -> None:
        self._baselines: list[BaselineReference] = []

    def add(self, baseline: BaselineReference) -> None:
        """
        Add a baseline reference to the history.

        Baselines are kept in chronological order by established_at.
        """
        if any(existing.id == baseline.id for existing in self._baselines):
            raise ValueError(
                f"Baseline with id '{baseline.id}' already exists."
            )

        self._baselines.append(baseline)
        self._baselines.sort(key=lambda item: item.established_at)

    def get(self, baseline_id: str) -> BaselineReference:
        """
        Retrieve a baseline by ID.
        """
        for baseline in self._baselines:
            if baseline.id == baseline_id:
                return baseline

        raise KeyError(
            f"Baseline with id '{baseline_id}' not found."
        )

    def all(self) -> list[BaselineReference]:
        """
        Return all baselines in chronological order.
        """
        return list(self._baselines)

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[BaselineReference]:
        """
        Return baselines established within the inclusive time range.
        """
        if start > end:
            raise ValueError("start must be before or equal to end")

        return [
            baseline
            for baseline in self._baselines
            if start <= baseline.established_at <= end
        ]

    def as_of(
        self,
        timestamp: datetime,
    ) -> list[BaselineReference]:
        """
        Return baselines established on or before a timestamp.
        """
        return [
            baseline
            for baseline in self._baselines
            if baseline.established_at <= timestamp
        ]

    def latest(
        self,
        timestamp: datetime | None = None,
    ) -> BaselineReference | None:
        """
        Return the latest baseline established at or before a timestamp.

        If no timestamp is supplied, return the latest baseline currently
        stored.
        """
        candidates = (
            self._baselines
            if timestamp is None
            else self.as_of(timestamp)
        )

        if not candidates:
            return None

        return candidates[-1]

    def valid_at(
        self,
        timestamp: datetime,
    ) -> list[BaselineReference]:
        """
        Return baselines whose declared validity interval contains
        the supplied timestamp.

        A baseline with no valid_from is considered valid from the
        beginning of the timeline.

        A baseline with no valid_to is considered valid indefinitely.
        """
        return [
            baseline
            for baseline in self._baselines
            if (
                (baseline.valid_from is None or baseline.valid_from <= timestamp)
                and
                (baseline.valid_to is None or timestamp <= baseline.valid_to)
            )
        ]

    def for_system(
        self,
        system_id: str,
    ) -> list[BaselineReference]:
        """
        Return all baselines belonging to a system.
        """
        return [
            baseline
            for baseline in self._baselines
            if baseline.system_id == system_id
        ]

    def for_dimension(
        self,
        system_id: str,
        dimension: str,
    ) -> list[BaselineReference]:
        """
        Return baselines for a specific system dimension.
        """
        return [
            baseline
            for baseline in self._baselines
            if (
                baseline.system_id == system_id
                and baseline.dimension == dimension
            )
        ]

    def __len__(self) -> int:
        return len(self._baselines)