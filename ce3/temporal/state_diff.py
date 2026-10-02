from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .state_version import StateVersion


class StateChange(BaseModel):
    """
    One structural change between two CE³ state versions.

    This model describes what changed. It does not decide whether
    the change is material, causal, important, or economically relevant.
    """

    path: str

    change_type: str

    previous_value: Any = None

    new_value: Any = None


class StateDiff(BaseModel):
    """
    Structural difference between two CE³ state versions.

    StateDiff identifies additions, removals, and modifications.
    It does not interpret the significance of those changes.
    """

    from_state_id: str

    to_state_id: str

    changes: list[StateChange] = Field(
        default_factory=list,
    )

    @property
    def changed(self) -> bool:
        """
        Whether any structural state change occurred.
        """

        return bool(self.changes)

    @classmethod
    def between(
        cls,
        previous: StateVersion,
        current: StateVersion,
    ) -> StateDiff:
        """
        Calculate the structural difference between two state versions.
        """

        changes: list[StateChange] = []

        cls._compare(
            previous.state,
            current.state,
            path="",
            changes=changes,
        )

        return cls(
            from_state_id=previous.id,
            to_state_id=current.id,
            changes=changes,
        )

    @classmethod
    def _compare(
        cls,
        previous: Any,
        current: Any,
        *,
        path: str,
        changes: list[StateChange],
    ) -> None:
        if isinstance(previous, dict) and isinstance(current, dict):
            previous_keys = set(previous)
            current_keys = set(current)

            for key in sorted(previous_keys - current_keys):
                child_path = cls._path(path, str(key))

                changes.append(
                    StateChange(
                        path=child_path,
                        change_type="removed",
                        previous_value=previous[key],
                        new_value=None,
                    )
                )

            for key in sorted(current_keys - previous_keys):
                child_path = cls._path(path, str(key))

                changes.append(
                    StateChange(
                        path=child_path,
                        change_type="added",
                        previous_value=None,
                        new_value=current[key],
                    )
                )

            for key in sorted(previous_keys & current_keys):
                cls._compare(
                    previous[key],
                    current[key],
                    path=cls._path(path, str(key)),
                    changes=changes,
                )

            return

        if isinstance(previous, list) and isinstance(current, list):
            if previous != current:
                changes.append(
                    StateChange(
                        path=path,
                        change_type="modified",
                        previous_value=previous,
                        new_value=current,
                    )
                )

            return

        if previous != current:
            changes.append(
                StateChange(
                    path=path,
                    change_type="modified",
                    previous_value=previous,
                    new_value=current,
                )
            )

    @staticmethod
    def _path(parent: str, child: str) -> str:
        if not parent:
            return child

        return f"{parent}.{child}"