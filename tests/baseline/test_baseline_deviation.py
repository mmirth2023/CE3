from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ce3.baseline.deviation import (
    BaselineDeviation,
    DeviationDirection,
)


UTC = timezone.utc


def test_baseline_deviation_can_be_created():
    observed_at = datetime(2026, 1, 15, tzinfo=UTC)

    deviation = BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        observed_at=observed_at,
        baseline_state={"production": 1000},
        observed_state={"production": 700},
        affected_paths=["production"],
        direction=DeviationDirection.BELOW,
        magnitude=0.30,
        persistence=0.80,
        confidence=0.95,
        rationale="Observed production is below the established baseline.",
        source_event_ids=["event-1"],
        source_observation_ids=["observation-1"],
    )

    assert deviation.id == "deviation-1"
    assert deviation.baseline_id == "baseline-1"
    assert deviation.system_id == "system-1"
    assert deviation.dimension == "production"
    assert deviation.observed_at == observed_at


def test_baseline_deviation_defaults_are_applied():
    deviation = BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        observed_at=datetime(2026, 1, 15, tzinfo=UTC),
    )

    assert deviation.baseline_state == {}
    assert deviation.observed_state == {}
    assert deviation.affected_paths == []
    assert deviation.direction == DeviationDirection.NONE
    assert deviation.magnitude == 0.0
    assert deviation.persistence == 0.0
    assert deviation.confidence == 0.0
    assert deviation.rationale == ""
    assert deviation.source_event_ids == []
    assert deviation.source_observation_ids == []
    assert deviation.metadata == {}


@pytest.mark.parametrize(
    "direction",
    [
        DeviationDirection.BELOW,
        DeviationDirection.ABOVE,
        DeviationDirection.MIXED,
        DeviationDirection.NONE,
    ],
)
def test_supported_deviation_directions(direction):
    deviation = BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        observed_at=datetime(2026, 1, 15, tzinfo=UTC),
        direction=direction,
    )

    assert deviation.direction == direction


def test_deviation_preserves_states_and_paths():
    deviation = BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="market",
        observed_at=datetime(2026, 1, 15, tzinfo=UTC),
        baseline_state={
            "price": 100,
            "volume": 1000,
        },
        observed_state={
            "price": 120,
            "volume": 1400,
        },
        affected_paths=[
            "market.price",
            "market.volume",
        ],
    )

    assert deviation.baseline_state == {
        "price": 100,
        "volume": 1000,
    }

    assert deviation.observed_state == {
        "price": 120,
        "volume": 1400,
    }

    assert deviation.affected_paths == [
        "market.price",
        "market.volume",
    ]


def test_deviation_preserves_lineage():
    deviation = BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        observed_at=datetime(2026, 1, 15, tzinfo=UTC),
        source_event_ids=["event-1", "event-2"],
        source_observation_ids=[
            "observation-1",
            "observation-2",
        ],
    )

    assert deviation.source_event_ids == [
        "event-1",
        "event-2",
    ]

    assert deviation.source_observation_ids == [
        "observation-1",
        "observation-2",
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("magnitude", -0.1),
        ("persistence", -0.1),
        ("persistence", 1.1),
        ("confidence", -0.1),
        ("confidence", 1.1),
    ],
)
def test_invalid_numeric_values_are_rejected(field, value):
    with pytest.raises(ValidationError):
        BaselineDeviation(
            id="deviation-1",
            baseline_id="baseline-1",
            system_id="system-1",
            dimension="production",
            observed_at=datetime(2026, 1, 15, tzinfo=UTC),
            **{field: value},
        )


def test_metadata_is_preserved():
    deviation = BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        observed_at=datetime(2026, 1, 15, tzinfo=UTC),
        metadata={
            "comparison_method": "historical",
            "reference_period": "2020-2025",
        },
    )

    assert deviation.metadata == {
        "comparison_method": "historical",
        "reference_period": "2020-2025",
    }