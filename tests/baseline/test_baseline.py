from datetime import datetime, timezone

import pytest

from ce3.baseline.models import BaselineReference


def test_baseline_reference_can_be_created():
    baseline = BaselineReference(
        id="BASELINE-001",
        system_id="SYSTEM-001",
        dimension="production",
        established_at=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        reference_state={
            "capacity": 500_000,
            "utilization": 0.85,
        },
        stability=0.9,
        confidence=0.95,
    )

    assert baseline.id == "BASELINE-001"
    assert baseline.system_id == "SYSTEM-001"
    assert baseline.dimension == "production"
    assert baseline.reference_state["capacity"] == 500_000
    assert baseline.stability == 0.9
    assert baseline.confidence == 0.95


def test_baseline_reference_defaults_are_empty():
    baseline = BaselineReference(
        id="BASELINE-001",
        system_id="SYSTEM-001",
        dimension="market",
        established_at=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        stability=0.8,
        confidence=0.9,
    )

    assert baseline.reference_state == {}
    assert baseline.reference_observation_ids == []
    assert baseline.comparable_state_ids == []
    assert baseline.conditions == {}
    assert baseline.metadata == {}


def test_baseline_reference_supports_temporal_validity():
    baseline = BaselineReference(
        id="BASELINE-001",
        system_id="SYSTEM-001",
        dimension="production",
        established_at=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_from=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2025,
            12,
            31,
            tzinfo=timezone.utc,
        ),
        stability=0.8,
        confidence=0.9,
    )

    assert baseline.valid_from is not None
    assert baseline.valid_to is not None


def test_baseline_reference_preserves_supporting_evidence():
    baseline = BaselineReference(
        id="BASELINE-001",
        system_id="SYSTEM-001",
        dimension="production",
        established_at=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        reference_observation_ids=[
            "OBS-001",
            "OBS-002",
        ],
        comparable_state_ids=[
            "STATE-101",
            "STATE-102",
        ],
        stability=0.85,
        confidence=0.9,
    )

    assert baseline.reference_observation_ids == [
        "OBS-001",
        "OBS-002",
    ]

    assert baseline.comparable_state_ids == [
        "STATE-101",
        "STATE-102",
    ]


def test_baseline_reference_preserves_conditions():
    baseline = BaselineReference(
        id="BASELINE-001",
        system_id="SYSTEM-001",
        dimension="production",
        established_at=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        conditions={
            "demand": "normal",
            "maintenance": False,
            "sanctions": False,
        },
        stability=0.9,
        confidence=0.9,
    )

    assert baseline.conditions["demand"] == "normal"
    assert baseline.conditions["maintenance"] is False


@pytest.mark.parametrize(
    "field",
    [
        "stability",
        "confidence",
    ],
)
def test_baseline_reference_rejects_invalid_scores(field):
    values = {
        "id": "BASELINE-001",
        "system_id": "SYSTEM-001",
        "dimension": "production",
        "established_at": datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        "stability": 0.8,
        "confidence": 0.9,
    }

    values[field] = 1.5

    with pytest.raises(ValueError):
        BaselineReference(**values)