from datetime import datetime

import pytest

from ce3.baseline.deviation import (
    BaselineDeviation,
    DeviationDirection,
)
from ce3.baseline.response import (
    ResponseDirection,
    SystemResponse,
)
from ce3.baseline.response_analysis import (
    ResponseClassification,
)
from ce3.baseline.response_analysis_engine import (
    ResponseAnalysisEngine,
)


def make_deviation() -> BaselineDeviation:
    return BaselineDeviation(
        id="deviation-1",
        baseline_id="baseline-1",
        system_id="system-1",
        dimension="economic",
        observed_at=datetime(2026, 2, 1),
        baseline_state={
            "production": 100,
        },
        observed_state={
            "production": 120,
        },
        direction=DeviationDirection.ABOVE,
        magnitude=0.20,
        persistence=0.8,
        confidence=0.9,
    )


def make_response(
    *,
    before: dict,
    after: dict,
    direction: ResponseDirection,
    magnitude: float,
    persistence: float = 0.8,
) -> SystemResponse:
    return SystemResponse(
        id="response-1",
        system_id="system-1",
        dimension="economic",
        deviation_id="deviation-1",
        observed_at=datetime(2026, 2, 1, 1),
        response_state_before=before,
        response_state_after=after,
        direction=direction,
        magnitude=magnitude,
        persistence=persistence,
        confidence=0.9,
    )


def test_build_creates_response_analysis() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 110,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "production": 100,
        },
    )

    assert analysis.id == "analysis-1"
    assert analysis.deviation_id == "deviation-1"
    assert analysis.response_id == "response-1"
    assert analysis.system_id == "system-1"
    assert analysis.dimension == "economic"


def test_response_moving_toward_baseline_is_normalized() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 110,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "production": 100,
        },
    )

    assert analysis.classification == (
        ResponseClassification.NORMALIZED
    )


def test_response_moving_away_from_baseline_is_amplified() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 140,
        },
        direction=ResponseDirection.INCREASE,
        magnitude=0.20,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "production": 100,
        },
    )

    assert analysis.classification == (
        ResponseClassification.AMPLIFIED
    )


def test_response_reaching_baseline_is_normalized() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 100,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.20,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "production": 100,
        },
    )

    assert analysis.classification == (
        ResponseClassification.NORMALIZED
    )

    assert analysis.baseline_distance_after == 0.0


def test_unchanged_response_is_stable() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 120,
        },
        direction=ResponseDirection.NONE,
        magnitude=0.0,
        persistence=0.0,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "production": 100,
        },
    )

    assert analysis.classification == (
        ResponseClassification.STABLE
    )


def test_persistent_response_is_detected_without_baseline_state() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 120,
        },
        direction=ResponseDirection.NONE,
        magnitude=0.0,
        persistence=0.8,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
    )

    assert analysis.classification == (
        ResponseClassification.PERSISTENT
    )


def test_response_strength_is_distance_change() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 110,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "production": 100,
        },
    )

    assert analysis.baseline_distance_before == pytest.approx(0.20)
    assert analysis.baseline_distance_after == pytest.approx(0.10)
    assert analysis.response_strength == pytest.approx(0.10)


def test_nested_state_distance_is_supported() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "market": {
                "price": 120,
                "volume": 1000,
            }
        },
        after={
            "market": {
                "price": 110,
                "volume": 900,
            }
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        baseline_state={
            "market": {
                "price": 100,
                "volume": 1000,
            }
        },
    )

    assert analysis.baseline_distance_before == pytest.approx(0.10)
    assert analysis.baseline_distance_after == pytest.approx(0.10)


def test_lineage_is_preserved() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 110,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    response.affected_paths = [
        "economic.production",
    ]
    response.source_event_ids = [
        "event-1",
    ]
    response.source_observation_ids = [
        "observation-1",
    ]

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
    )

    assert analysis.affected_paths == [
        "economic.production",
    ]
    assert analysis.source_event_ids == [
        "event-1",
    ]
    assert analysis.source_observation_ids == [
        "observation-1",
    ]


def test_confidence_can_be_overridden() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 110,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
        confidence=0.75,
    )

    assert analysis.confidence == pytest.approx(0.75)


def test_response_confidence_is_used_by_default() -> None:
    engine = ResponseAnalysisEngine()

    deviation = make_deviation()

    response = make_response(
        before={
            "production": 120,
        },
        after={
            "production": 110,
        },
        direction=ResponseDirection.DECREASE,
        magnitude=0.10,
    )

    analysis = engine.build(
        analysis_id="analysis-1",
        deviation=deviation,
        response=response,
    )

    assert analysis.confidence == pytest.approx(0.9)