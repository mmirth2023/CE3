from datetime import datetime, timezone

import pytest

from ce3.baseline.engine import BaselineEngine
from ce3.baseline.models import BaselineReference


UTC = timezone.utc


def test_build_creates_baseline_reference():
    engine = BaselineEngine()

    established_at = datetime(2026, 1, 1, tzinfo=UTC)

    baseline = engine.build(
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        established_at=established_at,
        reference_state={"production": 100},
        reference_observation_ids=["obs-1", "obs-2"],
        comparable_state_ids=["state-1"],
        conditions={"capacity": "stable"},
        stability=0.9,
        confidence=0.95,
    )

    assert isinstance(baseline, BaselineReference)
    assert baseline.id == "baseline-1"
    assert baseline.system_id == "system-1"
    assert baseline.dimension == "production"
    assert baseline.established_at == established_at
    assert baseline.reference_state == {"production": 100}
    assert baseline.reference_observation_ids == ["obs-1", "obs-2"]
    assert baseline.comparable_state_ids == ["state-1"]
    assert baseline.conditions == {"capacity": "stable"}
    assert baseline.stability == 0.9
    assert baseline.confidence == 0.95


def test_build_applies_empty_defaults():
    engine = BaselineEngine()

    baseline = engine.build(
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        established_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert baseline.reference_state == {}
    assert baseline.reference_observation_ids == []
    assert baseline.comparable_state_ids == []
    assert baseline.conditions == {}
    assert baseline.metadata == {}


def test_build_preserves_temporal_validity():
    engine = BaselineEngine()

    valid_from = datetime(2026, 1, 10, tzinfo=UTC)
    valid_to = datetime(2026, 2, 10, tzinfo=UTC)

    baseline = engine.build(
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        established_at=datetime(2026, 1, 1, tzinfo=UTC),
        valid_from=valid_from,
        valid_to=valid_to,
    )

    assert baseline.valid_from == valid_from
    assert baseline.valid_to == valid_to


def test_build_preserves_metadata():
    engine = BaselineEngine()

    baseline = engine.build(
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="production",
        established_at=datetime(2026, 1, 1, tzinfo=UTC),
        metadata={"method": "historical_reference"},
    )

    assert baseline.metadata == {
        "method": "historical_reference"
    }


def test_build_from_historical_state():
    engine = BaselineEngine()

    baseline = engine.build_from_historical_state(
        baseline_id="baseline-historical",
        system_id="system-1",
        dimension="exports",
        established_at=datetime(2026, 1, 1, tzinfo=UTC),
        historical_state={"exports": 500},
        observation_ids=["obs-10"],
        comparable_state_ids=["state-10"],
        conditions={"market": "normal"},
        stability=0.8,
        confidence=0.9,
    )

    assert isinstance(baseline, BaselineReference)
    assert baseline.reference_state == {"exports": 500}
    assert baseline.reference_observation_ids == ["obs-10"]
    assert baseline.comparable_state_ids == ["state-10"]
    assert baseline.conditions == {"market": "normal"}
    assert baseline.stability == 0.8
    assert baseline.confidence == 0.9


def test_build_from_comparable_states():
    engine = BaselineEngine()

    baseline = engine.build_from_comparable_states(
        baseline_id="baseline-comparable",
        system_id="system-1",
        dimension="market",
        established_at=datetime(2026, 1, 1, tzinfo=UTC),
        reference_state={
            "price": 100,
            "volume": 1000,
        },
        comparable_state_ids=[
            "state-2019",
            "state-2021",
            "state-2024",
        ],
        conditions={"regime": "normal"},
    )

    assert isinstance(baseline, BaselineReference)
    assert baseline.reference_state == {
        "price": 100,
        "volume": 1000,
    }
    assert baseline.comparable_state_ids == [
        "state-2019",
        "state-2021",
        "state-2024",
    ]
    assert baseline.conditions == {"regime": "normal"}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("confidence", 1.5),
        ("confidence", -0.1),
        ("stability", 1.5),
        ("stability", -0.1),
    ],
)
def test_build_rejects_invalid_scores(field, value):
    engine = BaselineEngine()

    kwargs = {
        "baseline_id": "baseline-invalid",
        "system_id": "system-1",
        "dimension": "production",
        "established_at": datetime(2026, 1, 1, tzinfo=UTC),
        field: value,
    }

    with pytest.raises(ValueError):
        engine.build(**kwargs)