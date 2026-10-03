from __future__ import annotations

from datetime import datetime

from .models import PropagationPath


class PropagationHistory:
    """
    Temporal history of canonical propagation paths.

    PropagationHistory stores propagation paths in chronological order
    and provides deterministic temporal queries.

    It does not infer propagation, determine causality, assess materiality,
    or predict future outcomes.
    """

    def __init__(self) -> None:
        self._paths: list[PropagationPath] = []

    def add(self, path: PropagationPath) -> None:
        """
        Add a propagation path to the history.

        Paths are kept in chronological order by identified_at.
        """
        if any(existing.id == path.id for existing in self._paths):
            raise ValueError(
                f"Propagation path with id '{path.id}' already exists."
            )

        self._paths.append(path)
        self._paths.sort(key=lambda item: item.identified_at)

    def get(self, path_id: str) -> PropagationPath:
        """
        Retrieve a propagation path by ID.
        """
        for path in self._paths:
            if path.id == path_id:
                return path

        raise KeyError(
            f"Propagation path with id '{path_id}' not found."
        )

    def all(self) -> list[PropagationPath]:
        """
        Return all propagation paths in chronological order.
        """
        return list(self._paths)

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[PropagationPath]:
        """
        Return paths identified within the inclusive time range.
        """
        if start > end:
            raise ValueError(
                "start must be before or equal to end"
            )

        return [
            path
            for path in self._paths
            if start <= path.identified_at <= end
        ]

    def as_of(
        self,
        timestamp: datetime,
    ) -> list[PropagationPath]:
        """
        Return paths identified on or before a timestamp.
        """
        return [
            path
            for path in self._paths
            if path.identified_at <= timestamp
        ]

    def latest(
        self,
        timestamp: datetime | None = None,
    ) -> PropagationPath | None:
        """
        Return the latest path identified at or before a timestamp.

        If no timestamp is supplied, return the latest path currently
        stored.
        """
        candidates = (
            self._paths
            if timestamp is None
            else self.as_of(timestamp)
        )

        if not candidates:
            return None

        return candidates[-1]

    def valid_at(
        self,
        timestamp: datetime,
    ) -> list[PropagationPath]:
        """
        Return paths whose declared validity interval contains
        the supplied timestamp.

        A path with no valid_from is considered valid from the
        beginning of the timeline.

        A path with no valid_to is considered valid indefinitely.
        """
        return [
            path
            for path in self._paths
            if (
                (
                    path.valid_from is None
                    or path.valid_from <= timestamp
                )
                and
                (
                    path.valid_to is None
                    or timestamp <= path.valid_to
                )
            )
        ]

    def from_source(
        self,
        source_id: str,
    ) -> list[PropagationPath]:
        """
        Return paths originating from a source.
        """
        return [
            path
            for path in self._paths
            if path.source_id == source_id
        ]

    def to_target(
        self,
        target_id: str,
    ) -> list[PropagationPath]:
        """
        Return paths terminating at a target.
        """
        return [
            path
            for path in self._paths
            if path.target_id == target_id
        ]

    def between_nodes(
        self,
        source_id: str,
        target_id: str,
    ) -> list[PropagationPath]:
        """
        Return paths connecting a specific source and target.
        """
        return [
            path
            for path in self._paths
            if (
                path.source_id == source_id
                and path.target_id == target_id
            )
        ]

    def affecting(
        self,
        entity_id: str,
    ) -> list[PropagationPath]:
        """
        Return paths where the supplied entity appears as a source,
        target, or intermediate node.
        """
        return [
            path
            for path in self._paths
            if (
                path.source_id == entity_id
                or path.target_id == entity_id
                or entity_id in path.intermediate_ids
            )
        ]

    def by_relationship(
        self,
        relationship_id: str,
    ) -> list[PropagationPath]:
        """
        Return paths associated with a relationship.
        """
        return [
            path
            for path in self._paths
            if path.relationship_id == relationship_id
        ]

    def by_dependency(
        self,
        dependency_id: str,
    ) -> list[PropagationPath]:
        """
        Return paths associated with a dependency.
        """
        return [
            path
            for path in self._paths
            if path.dependency_id == dependency_id
        ]

    def __len__(self) -> int:
        return len(self._paths)