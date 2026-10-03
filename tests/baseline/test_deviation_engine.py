from datetime import datetime

import pytest

from ce3.baseline.deviation import DeviationDirection
from ce3.baseline.deviation_engine import DeviationEngine
from ce3.baseline.models import BaselineReference


def make_baseline(
    *,
    reference_state: dict,
) -> BaselineReference:
    return BaselineReference(
        id="baseline-1",
        system_id="system-1",
        dimension="economic",
        established_at=datetime(2026, 1, 1),
        reference_state=reference_state,
        stability=0.9,
        confidence=0.9,
    )


def test_build_creates_baseline_deviation() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
            "exports": 100,
        },
    )

    assert deviation.id == "deviation-1"
    assert deviation.baseline_id == "baseline-1"
    assert deviation.system_id == "system-1"
    assert deviation.dimension == "economic"
    assert deviation.observed_at == datetime(2026, 2, 1)


def test_build_preserves_baseline_and_observed_state() -> None:
    engine = DeviationEngine()

    baseline_state = {
        "production": 100,
        "exports": 80,
    }

    observed_state = {
        "production": 120,
        "exports": 70,
    }

    baseline = make_baseline(
        reference_state=baseline_state,
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state=observed_state,
    )

    assert deviation.baseline_state == baseline_state
    assert deviation.observed_state == observed_state


def test_all_values_above_baseline_are_above() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
            "exports": 100,
        },
    )

    assert deviation.direction == DeviationDirection.ABOVE


def test_all_values_below_baseline_are_below() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 90,
            "exports": 60,
        },
    )

    assert deviation.direction == DeviationDirection.BELOW


def test_mixed_values_produce_mixed_direction() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
            "exports": 60,
        },
    )

    assert deviation.direction == DeviationDirection.MIXED


def test_unchanged_values_produce_no_deviation() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 100,
            "exports": 80,
        },
    )

    assert deviation.direction == DeviationDirection.NONE
    assert deviation.magnitude == 0.0


def test_magnitude_is_average_absolute_relative_deviation() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
            "exports": 100,
        },
    )

    expected = (
        (20 / 100)
        + (20 / 80)
    ) / 2

    assert deviation.magnitude == pytest.approx(expected)


def test_nested_numeric_values_are_compared() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "market": {
                "price": 100,
                "volume": 1000,
            }
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "market": {
                "price": 110,
                "volume": 1200,
            }
        },
    )

    assert deviation.direction == DeviationDirection.ABOVE
    assert deviation.magnitude == pytest.approx(
        ((10 / 100) + (200 / 1000)) / 2
    )


def test_non_numeric_fields_do_not_contribute_to_magnitude() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "status": "normal",
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
            "status": "disrupted",
        },
    )

    assert deviation.direction == DeviationDirection.ABOVE
    assert deviation.magnitude == pytest.approx(0.20)


def test_boolean_values_are_not_treated_as_numeric() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "active": True,
            "production": 100,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "active": False,
            "production": 120,
        },
    )

    assert deviation.direction == DeviationDirection.ABOVE
    assert deviation.magnitude == pytest.approx(0.20)


def test_missing_fields_are_not_compared() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
            "exports": 80,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
        },
    )

    assert deviation.direction == DeviationDirection.ABOVE
    assert deviation.magnitude == pytest.approx(0.20)


def test_zero_baseline_does_not_create_relative_magnitude() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 0,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 50,
        },
    )

    assert deviation.magnitude == 0.0


def test_lineage_and_metadata_are_preserved() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
        }
    )

    deviation = engine.build(
        deviation_id="deviation-1",
        baseline=baseline,
        observed_at=datetime(2026, 2, 1),
        observed_state={
            "production": 120,
        },
        affected_paths=[
            "economic.production",
        ],
        persistence=0.75,
        confidence=0.85,
        rationale="Observed production exceeds established baseline.",
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

    assert deviation.affected_paths == [
        "economic.production",
    ]
    assert deviation.persistence == 0.75
    assert deviation.confidence == 0.85
    assert deviation.rationale == (
        "Observed production exceeds established baseline."
    )
    assert deviation.source_event_ids == [
        "event-1",
    ]
    assert deviation.source_observation_ids == [
        "observation-1",
    ]
    assert deviation.metadata == {
        "test": True,
    }


def test_invalid_persistence_is_rejected() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
        }
    )

    with pytest.raises(ValueError):
        engine.build(
            deviation_id="deviation-1",
            baseline=baseline,
            observed_at=datetime(2026, 2, 1),
            observed_state={
                "production": 120,
            },
            persistence=1.5,
        )


def test_invalid_confidence_is_rejected() -> None:
    engine = DeviationEngine()

    baseline = make_baseline(
        reference_state={
            "production": 100,
        }
    )

    with pytest.raises(ValueError):
        engine.build(
            deviation_id="deviation-1",
            baseline=baseline,
            observed_at=datetime(2026, 2, 1),
            observed_state={
                "production": 120,
            },
            confidence=-0.1,
        )