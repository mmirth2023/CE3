from datetime import datetime

import pytest

from ce3.baseline.response import ResponseDirection, SystemResponse


def make_response(
    *,
    before: dict,
    after: dict,
) -> SystemResponse:
    return SystemResponse(
        id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        response_state_before=before,
        response_state_after=after,
        direction=ResponseDirection.INCREASE,
        magnitude=0.25,
        latency_seconds=300.0,
        persistence=0.8,
        confidence=0.9,
    )


def test_response_can_be_created() -> None:
    response = make_response(
        before={
            "production": 100,
        },
        after={
            "production": 125,
        },
    )

    assert response.id == "response-1"
    assert response.system_id == "system-1"
    assert response.dimension == "economic"
    assert response.deviation_id == "deviation-1"
    assert response.observed_at == datetime(2026, 2, 1)


def test_response_preserves_before_and_after_states() -> None:
    before = {
        "production": 100,
        "exports": 80,
    }

    after = {
        "production": 75,
        "exports": 60,
    }

    response = make_response(
        before=before,
        after=after,
    )

    assert response.response_state_before == before
    assert response.response_state_after == after


def test_response_direction_is_preserved() -> None:
    response = make_response(
        before={
            "production": 100,
        },
        after={
            "production": 125,
        },
    )

    assert response.direction == ResponseDirection.INCREASE


def test_response_magnitude_is_preserved() -> None:
    response = make_response(
        before={
            "production": 100,
        },
        after={
            "production": 125,
        },
    )

    assert response.magnitude == pytest.approx(0.25)


def test_response_latency_is_preserved() -> None:
    response = make_response(
        before={
            "production": 100,
        },
        after={
            "production": 125,
        },
    )

    assert response.latency_seconds == pytest.approx(300.0)


def test_response_persistence_and_confidence_are_preserved() -> None:
    response = make_response(
        before={
            "production": 100,
        },
        after={
            "production": 125,
        },
    )

    assert response.persistence == pytest.approx(0.8)
    assert response.confidence == pytest.approx(0.9)


def test_response_lineage_is_preserved() -> None:
    response = SystemResponse(
        id="response-2",
        system_id="system-1",
        dimension="financial",
        deviation_id="deviation-2",
        observed_at=datetime(2026, 2, 1),
        response_state_before={
            "price": 100,
        },
        response_state_after={
            "price": 110,
        },
        direction=ResponseDirection.INCREASE,
        magnitude=0.10,
        latency_seconds=120.0,
        persistence=0.7,
        confidence=0.85,
        affected_paths=[
            "financial.price",
        ],
        rationale="Observed price response following state deviation.",
        source_event_ids=[
            "event-1",
        ],
        source_observation_ids=[
            "observation-1",
        ],
        metadata={
            "test": True,
        },
    )

    assert response.affected_paths == [
        "financial.price",
    ]

    assert response.rationale == (
        "Observed price response following state deviation."
    )

    assert response.source_event_ids == [
        "event-1",
    ]

    assert response.source_observation_ids == [
        "observation-1",
    ]

    assert response.metadata == {
        "test": True,
    }


def test_invalid_magnitude_is_rejected() -> None:
    with pytest.raises(ValueError):
        SystemResponse(
            id="response-1",
            system_id="system-1",
            dimension="economic",
            deviation_id="deviation-1",
            observed_at=datetime(2026, 2, 1),
            magnitude=-0.1,
        )


def test_invalid_latency_is_rejected() -> None:
    with pytest.raises(ValueError):
        SystemResponse(
            id="response-1",
            system_id="system-1",
            dimension="economic",
            deviation_id="deviation-1",
            observed_at=datetime(2026, 2, 1),
            latency_seconds=-1.0,
        )


def test_invalid_persistence_is_rejected() -> None:
    with pytest.raises(ValueError):
        SystemResponse(
            id="response-1",
            system_id="system-1",
            dimension="economic",
            deviation_id="deviation-1",
            observed_at=datetime(2026, 2, 1),
            persistence=1.5,
        )


def test_invalid_confidence_is_rejected() -> None:
    with pytest.raises(ValueError):
        SystemResponse(
            id="response-1",
            system_id="system-1",
            dimension="economic",
            deviation_id="deviation-1",
            observed_at=datetime(2026, 2, 1),
            confidence=-0.1,
        )


def test_default_values_are_applied() -> None:
    response = SystemResponse(
        id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
    )

    assert response.response_state_before == {}
    assert response.response_state_after == {}
    assert response.affected_paths == []
    assert response.direction == ResponseDirection.NONE
    assert response.magnitude == 0.0
    assert response.latency_seconds == 0.0
    assert response.persistence == 0.0
    assert response.confidence == 0.0
    assert response.rationale == ""
    assert response.source_event_ids == []
    assert response.source_observation_ids == []
    assert response.metadata == {}