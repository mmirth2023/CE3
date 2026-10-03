from datetime import datetime, timezone

import pytest

from ce3.system.history import GlobalSystemStateHistory
from ce3.system.models import GlobalSystemState


def make_state(
    state_id: str,
    year: int,
) -> GlobalSystemState:
    return GlobalSystemState(
        id=state_id,
        state_time=datetime(
            year,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )


def test_global_system_state_history_adds_state():
    history = GlobalSystemStateHistory()

    state = make_state(
        "STATE-001",
        2020,
    )

    stored = history.add(state)

    assert stored is state
    assert len(history) == 1


def test_global_system_state_history_rejects_duplicate_ids():
    history = GlobalSystemStateHistory()

    state = make_state(
        "STATE-001",
        2020,
    )

    history.add(state)

    with pytest.raises(ValueError):
        history.add(state)


def test_global_system_state_history_gets_state_by_id():
    history = GlobalSystemStateHistory()

    state = make_state(
        "STATE-001",
        2020,
    )

    history.add(state)

    assert history.get("STATE-001") is state


def test_global_system_state_history_rejects_unknown_id():
    history = GlobalSystemStateHistory()

    with pytest.raises(KeyError):
        history.get("STATE-404")


def test_global_system_state_history_returns_chronological_order():
    history = GlobalSystemStateHistory()

    later = make_state(
        "STATE-002",
        2025,
    )

    earlier = make_state(
        "STATE-001",
        2020,
    )

    history.add(later)
    history.add(earlier)

    assert history.all() == [
        earlier,
        later,
    ]


def test_global_system_state_history_between_returns_states_in_period():
    history = GlobalSystemStateHistory()

    first = make_state(
        "STATE-001",
        2020,
    )

    middle = make_state(
        "STATE-002",
        2025,
    )

    last = make_state(
        "STATE-003",
        2030,
    )

    history.add(first)
    history.add(middle)
    history.add(last)

    result = history.between(
        datetime(
            2024,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert result == [middle]


def test_global_system_state_history_as_of_reconstructs_known_states():
    history = GlobalSystemStateHistory()

    first = make_state(
        "STATE-001",
        2020,
    )

    second = make_state(
        "STATE-002",
        2025,
    )

    third = make_state(
        "STATE-003",
        2030,
    )

    history.add(first)
    history.add(second)
    history.add(third)

    result = history.as_of(
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result == [
        first,
        second,
    ]


def test_global_system_state_history_latest_returns_latest_state():
    history = GlobalSystemStateHistory()

    first = make_state(
        "STATE-001",
        2020,
    )

    second = make_state(
        "STATE-002",
        2025,
    )

    history.add(first)
    history.add(second)

    assert history.latest() is second


def test_global_system_state_history_latest_can_be_temporal():
    history = GlobalSystemStateHistory()

    first = make_state(
        "STATE-001",
        2020,
    )

    second = make_state(
        "STATE-002",
        2025,
    )

    third = make_state(
        "STATE-003",
        2030,
    )

    history.add(first)
    history.add(second)
    history.add(third)

    result = history.latest(
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert result is second


def test_global_system_state_history_latest_returns_none_when_empty():
    history = GlobalSystemStateHistory()

    assert history.latest() is None