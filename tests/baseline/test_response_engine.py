from datetime import datetime, timedelta

import pytest

from ce3.baseline.response import ResponseDirection
from ce3.baseline.response_engine import ResponseEngine


def test_build_creates_response() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1, 12, 5),
        state_before={
            "production": 100,
        },
        state_after={
            "production": 120,
        },
    )

    assert response.id == "response-1"
    assert response.system_id == "system-1"
    assert response.dimension == "economic"
    assert response.deviation_id == "deviation-1"
    assert response.observed_at == datetime(2026, 2, 1, 12, 5)


def test_increase_is_detected() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
        },
        state_after={
            "production": 120,
        },
    )

    assert response.direction == ResponseDirection.INCREASE


def test_decrease_is_detected() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
        },
        state_after={
            "production": 80,
        },
    )

    assert response.direction == ResponseDirection.DECREASE


def test_mixed_response_is_detected() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
            "exports": 80,
        },
        state_after={
            "production": 120,
            "exports": 60,
        },
    )

    assert response.direction == ResponseDirection.MIXED


def test_unchanged_state_has_no_response() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
        },
        state_after={
            "production": 100,
        },
    )

    assert response.direction == ResponseDirection.NONE
    assert response.magnitude == 0.0


def test_magnitude_is_average_absolute_relative_change() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
            "exports": 80,
        },
        state_after={
            "production": 120,
            "exports": 100,
        },
    )

    expected = (
        (20 / 100)
        + (20 / 80)
    ) / 2

    assert response.magnitude == pytest.approx(expected)


def test_nested_numeric_values_are_compared() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="financial",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "market": {
                "price": 100,
                "volume": 1000,
            }
        },
        state_after={
            "market": {
                "price": 110,
                "volume": 1200,
            }
        },
    )

    assert response.direction == ResponseDirection.INCREASE
    assert response.magnitude == pytest.approx(
        ((10 / 100) + (200 / 1000)) / 2
    )


def test_non_numeric_fields_do_not_contribute() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
            "status": "normal",
        },
        state_after={
            "production": 120,
            "status": "disrupted",
        },
    )

    assert response.direction == ResponseDirection.INCREASE
    assert response.magnitude == pytest.approx(0.20)


def test_boolean_values_are_not_numeric() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "active": True,
            "production": 100,
        },
        state_after={
            "active": False,
            "production": 120,
        },
    )

    assert response.direction == ResponseDirection.INCREASE
    assert response.magnitude == pytest.approx(0.20)


def test_missing_fields_are_not_compared() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
            "exports": 80,
        },
        state_after={
            "production": 120,
        },
    )

    assert response.direction == ResponseDirection.INCREASE
    assert response.magnitude == pytest.approx(0.20)


def test_latency_is_calculated() -> None:
    engine = ResponseEngine()

    previous = datetime(2026, 2, 1, 12, 0)
    current = previous + timedelta(minutes=5)

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=current,
        previous_observed_at=previous,
        state_before={
            "production": 100,
        },
        state_after={
            "production": 120,
        },
    )

    assert response.latency_seconds == pytest.approx(300.0)


def test_missing_previous_timestamp_gives_zero_latency() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 100,
        },
        state_after={
            "production": 120,
        },
    )

    assert response.latency_seconds == 0.0


def test_invalid_latency_order_is_rejected() -> None:
    engine = ResponseEngine()

    with pytest.raises(ValueError):
        engine.build(
            response_id="response-1",
            system_id="system-1",
            dimension="economic",
            deviation_id="deviation-1",
            observed_at=datetime(2026, 2, 1),
            previous_observed_at=datetime(2026, 2, 2),
            state_before={
                "production": 100,
            },
            state_after={
                "production": 120,
            },
        )


def test_lineage_and_metadata_are_preserved() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="financial",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "price": 100,
        },
        state_after={
            "price": 110,
        },
        affected_paths=[
            "financial.price",
        ],
        persistence=0.75,
        confidence=0.85,
        rationale="Observed financial response.",
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
    assert response.persistence == pytest.approx(0.75)
    assert response.confidence == pytest.approx(0.85)
    assert response.rationale == "Observed financial response."
    assert response.source_event_ids == [
        "event-1",
    ]
    assert response.source_observation_ids == [
        "observation-1",
    ]
    assert response.metadata == {
        "test": True,
    }


def test_zero_baseline_does_not_create_relative_magnitude() -> None:
    engine = ResponseEngine()

    response = engine.build(
        response_id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1),
        state_before={
            "production": 0,
        },
        state_after={
            "production": 50,
        },
    )

    assert response.magnitude == 0.0