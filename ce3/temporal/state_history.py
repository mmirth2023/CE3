from __future__ import annotations

from datetime import datetime

from .state_version import StateVersion


class StateHistory:
    """
    Chronological history of CE³ canonical state versions.

    StateHistory stores immutable logical snapshots and provides
    deterministic temporal queries over those snapshots.

    It does not determine state, calculate differences, or interpret
    why a state changed. Those responsibilities belong to higher layers.
    """

    def __init__(self) -> None:
        self._versions: dict[str, StateVersion] = {}

    def add(self, version: StateVersion) -> None:
        """
        Add a state version.

        State version IDs must be unique.
        """

        if version.id in self._versions:
            raise ValueError(
                f"State version already exists: {version.id}"
            )

        self._versions[version.id] = version

    def get(self, version_id: str) -> StateVersion:
        """
        Retrieve a state version by ID.
        """

        try:
            return self._versions[version_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown state version: {version_id}"
            ) from exc

    def all(self) -> list[StateVersion]:
        """
        Return all state versions chronologically.
        """

        return sorted(
            self._versions.values(),
            key=lambda version: version.state_time,
        )

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[StateVersion]:
        """
        Return state versions whose state_time falls within
        the inclusive interval [start, end].
        """

        return [
            version
            for version in self.all()
            if start <= version.state_time <= end
        ]

    def as_of(self, timestamp: datetime) -> list[StateVersion]:
        """
        Return all state versions known at or before timestamp.

        This is the core temporal query used to avoid hindsight.
        """

        return [
            version
            for version in self.all()
            if version.state_time <= timestamp
        ]

    def latest(
        self,
        timestamp: datetime | None = None,
    ) -> StateVersion | None:
        """
        Return the latest state version.

        When timestamp is supplied, only versions at or before that
        timestamp are considered.
        """

        versions = (
            self.all()
            if timestamp is None
            else self.as_of(timestamp)
        )

        if not versions:
            return None

        return versions[-1]

    def __len__(self) -> int:
        return len(self._versions)