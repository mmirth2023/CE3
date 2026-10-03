from datetime import datetime, timezone

import pytest

from ce3.system.models import GlobalSystemState


def test_global_system_state_can_be_created():
    state = GlobalSystemState(
        id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    assert state.id == "STATE-001"
    assert state.confidence == 0.9


def test_global_system_state_initializes_all_dimensions():
    state = GlobalSystemState(
        id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        confidence=0.9,
    )

    assert state.entities == {}
    assert state.relationships == {}
    assert state.physical == {}
    assert state.economic == {}
    assert state.financial == {}
    assert state.political == {}
    assert state.information == {}
    assert state.infrastructure == {}
    assert state.market == {}
    assert state.constraints == {}
    assert state.dependencies == {}
    assert state.active_shocks == {}
    assert state.observability == {}
    assert state.adaptations == {}
    assert state.propagation_paths == {}


def test_global_system_state_preserves_structured_dimensions():
    state = GlobalSystemState(
        id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        physical={
            "oil_production": {
                "status": "reduced",
                "capacity": 500_000,
            },
        },
        market={
            "brent": {
                "price": 85.0,
            },
        },
        confidence=0.8,
    )

    assert state.physical["oil_production"]["status"] == "reduced"
    assert state.market["brent"]["price"] == 85.0


def test_global_system_state_preserves_source_lineage():
    state = GlobalSystemState(
        id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        source_event_ids=[
            "EVENT-001",
            "EVENT-002",
        ],
        source_observation_ids=[
            "OBS-001",
        ],
        confidence=0.9,
    )

    assert state.source_event_ids == [
        "EVENT-001",
        "EVENT-002",
    ]

    assert state.source_observation_ids == [
        "OBS-001",
    ]


def test_global_system_state_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        GlobalSystemState(
            id="STATE-001",
            state_time=datetime(
                2025,
                1,
                1,
                tzinfo=timezone.utc,
            ),
            confidence=1.5,
        )


def test_global_system_state_preserves_uncertainty():
    state = GlobalSystemState(
        id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        uncertainty={
            "production_capacity": {
                "range": [
                    400_000,
                    500_000,
                ],
                "reason": "incomplete observation",
            },
        },
        confidence=0.7,
    )

    assert (
        state.uncertainty["production_capacity"]["range"]
        == [400_000, 500_000]
    )


def test_global_system_state_supports_active_shocks():
    state = GlobalSystemState(
        id="STATE-001",
        state_time=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        active_shocks={
            "SHOCK-001": {
                "type": "facility_damage",
                "severity": "high",
            },
        },
        confidence=0.9,
    )

    assert state.active_shocks["SHOCK-001"]["type"] == (
        "facility_damage"
    )