from datetime import datetime, timedelta, timezone

import pytest

from ce3.baseline.history import BaselineHistory
from ce3.baseline.models import BaselineReference


UTC = timezone.utc


def make_baseline(
    baseline_id: str,
    established_at: datetime,
    *,
    system_id: str = "system-1",
    dimension: str = "production",
    valid_from: datetime | None = None,
    valid_to: datetime | None = None,
) -> BaselineReference:
    return BaselineReference(
        id=baseline_id,
        system_id=system_id,
        dimension=dimension,
        established_at=established_at,
        valid_from=valid_from,
        valid_to=valid_to,
        reference_state={"level": 100},
        stability=0.9,
        confidence=0.95,
    )


def test_add_and_get_baseline():
    history = BaselineHistory()

    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    baseline = make_baseline(
        "baseline-1",
        timestamp,
    )

    history.add(baseline)

    assert history.get("baseline-1") == baseline
    assert len(history) == 1


def test_duplicate_baseline_id_is_rejected():
    history = BaselineHistory()

    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    history.add(
        make_baseline(
            "baseline-1",
            timestamp,
        )
    )

    with pytest.raises(ValueError):
        history.add(
            make_baseline(
                "baseline-1",
                timestamp + timedelta(days=1),
            )
        )


def test_baselines_are_kept_in_chronological_order():
    history = BaselineHistory()

    first = datetime(2026, 1, 1, tzinfo=UTC)
    second = datetime(2026, 2, 1, tzinfo=UTC)
    third = datetime(2026, 3, 1, tzinfo=UTC)

    history.add(make_baseline("baseline-3", third))
    history.add(make_baseline("baseline-1", first))
    history.add(make_baseline("baseline-2", second))

    assert [
        baseline.id
        for baseline in history.all()
    ] == [
        "baseline-1",
        "baseline-2",
        "baseline-3",
    ]


def test_between_returns_inclusive_range():
    history = BaselineHistory()

    first = datetime(2026, 1, 1, tzinfo=UTC)
    second = datetime(2026, 2, 1, tzinfo=UTC)
    third = datetime(2026, 3, 1, tzinfo=UTC)

    history.add(make_baseline("baseline-1", first))
    history.add(make_baseline("baseline-2", second))
    history.add(make_baseline("baseline-3", third))

    results = history.between(second, third)

    assert [
        baseline.id
        for baseline in results
    ] == [
        "baseline-2",
        "baseline-3",
    ]


def test_between_rejects_invalid_range():
    history = BaselineHistory()

    start = datetime(2026, 2, 1, tzinfo=UTC)
    end = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(ValueError):
        history.between(start, end)


def test_as_of_returns_established_baselines():
    history = BaselineHistory()

    first = datetime(2026, 1, 1, tzinfo=UTC)
    second = datetime(2026, 2, 1, tzinfo=UTC)
    third = datetime(2026, 3, 1, tzinfo=UTC)

    history.add(make_baseline("baseline-1", first))
    history.add(make_baseline("baseline-2", second))
    history.add(make_baseline("baseline-3", third))

    results = history.as_of(second)

    assert [
        baseline.id
        for baseline in results
    ] == [
        "baseline-1",
        "baseline-2",
    ]


def test_latest_returns_latest_baseline_as_of_timestamp():
    history = BaselineHistory()

    first = datetime(2026, 1, 1, tzinfo=UTC)
    second = datetime(2026, 2, 1, tzinfo=UTC)
    third = datetime(2026, 3, 1, tzinfo=UTC)

    history.add(make_baseline("baseline-1", first))
    history.add(make_baseline("baseline-2", second))
    history.add(make_baseline("baseline-3", third))

    assert history.latest(second).id == "baseline-2"


def test_latest_returns_none_when_history_is_empty():
    history = BaselineHistory()

    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    assert history.latest(timestamp) is None


def test_valid_at_respects_validity_window():
    history = BaselineHistory()

    valid_from = datetime(2026, 1, 10, tzinfo=UTC)
    valid_to = datetime(2026, 1, 20, tzinfo=UTC)

    baseline = make_baseline(
        "baseline-1",
        datetime(2026, 1, 1, tzinfo=UTC),
        valid_from=valid_from,
        valid_to=valid_to,
    )

    history.add(baseline)

    assert history.valid_at(
        datetime(2026, 1, 15, tzinfo=UTC)
    ) == [baseline]

    assert history.valid_at(
        datetime(2026, 1, 25, tzinfo=UTC)
    ) == []


def test_valid_at_supports_open_ended_validity():
    history = BaselineHistory()

    baseline = make_baseline(
        "baseline-1",
        datetime(2026, 1, 1, tzinfo=UTC),
        valid_from=datetime(2026, 1, 10, tzinfo=UTC),
    )

    history.add(baseline)

    assert history.valid_at(
        datetime(2026, 2, 1, tzinfo=UTC)
    ) == [baseline]


def test_for_system_filters_correctly():
    history = BaselineHistory()

    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    history.add(
        make_baseline(
            "baseline-1",
            timestamp,
            system_id="system-1",
        )
    )

    history.add(
        make_baseline(
            "baseline-2",
            timestamp + timedelta(days=1),
            system_id="system-2",
        )
    )

    results = history.for_system("system-1")

    assert [baseline.id for baseline in results] == ["baseline-1"]


def test_for_dimension_filters_system_and_dimension():
    history = BaselineHistory()

    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    history.add(
        make_baseline(
            "baseline-1",
            timestamp,
            system_id="system-1",
            dimension="production",
        )
    )

    history.add(
        make_baseline(
            "baseline-2",
            timestamp + timedelta(days=1),
            system_id="system-1",
            dimension="exports",
        )
    )

    history.add(
        make_baseline(
            "baseline-3",
            timestamp + timedelta(days=2),
            system_id="system-2",
            dimension="production",
        )
    )

    results = history.for_dimension(
        "system-1",
        "production",
    )

    assert [baseline.id for baseline in results] == ["baseline-1"]


def test_missing_baseline_raises_key_error():
    history = BaselineHistory()

    with pytest.raises(KeyError):
        history.get("does-not-exist")