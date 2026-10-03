from datetime import datetime, timezone

import pytest

from ce3.change.engine import StateChangeEngine
from ce3.materiality.models import MaterialityLevel
from ce3.systemic.engine import SystemicChangeEngine
from ce3.systemic.models import SystemicLevel
from ce3.temporal.state_diff import StateDiff
from ce3.temporal.state_version import StateVersion


def make_version(
    version_id: str,
    status: str,
) -> StateVersion:
    return StateVersion(
        id=version_id,
        state_time=datetime(
            2026,
            10,
            2,
            15,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        state={
            "facility_A": {
                "status": status,
            },
        },
        confidence=0.9,
    )


def make_material_state_change():
    previous = make_version(
        "STATE-001",
        "operational",
    )

    current = make_version(
        "STATE-002",
        "degraded",
    )

    diff = StateDiff.between(
        previous,
        current,
    )

    engine = StateChangeEngine()

    return engine.assess(
        change_id="CHANGE-001",
        diff=diff,
        assessed_at=datetime(
            2026,
            10,
            2,
            15,
            5,
            0,
            tzinfo=timezone.utc,
        ),
        magnitude=0.8,
        structural_relevance=0.9,
        persistence=0.7,
        confidence=0.9,
    )


def test_systemic_change_engine_identifies_systemic_change():
    state_change = make_material_state_change()

    assert state_change.materiality.level == (
        MaterialityLevel.CRITICAL
    )

    engine = SystemicChangeEngine()

    assessment = engine.assess(
        change_id="SYSTEMIC-001",
        state_change=state_change,
        assessed_at=datetime(
            2026,
            10,
            2,
            15,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        scope=0.9,
        dependency_relevance=0.9,
        cross_domain_relevance=0.8,
        persistence=0.8,
        confidence=0.9,
    )

    assert assessment.id == "SYSTEMIC-001"
    assert assessment.state_change is state_change
    assert assessment.level == SystemicLevel.SYSTEMIC
    assert assessment.is_systemic is True


def test_systemic_change_engine_identifies_local_change():
    state_change = make_material_state_change()

    engine = SystemicChangeEngine()

    assessment = engine.assess(
        change_id="SYSTEMIC-002",
        state_change=state_change,
        assessed_at=datetime.now(timezone.utc),
        scope=0.3,
        dependency_relevance=0.3,
        cross_domain_relevance=0.2,
        persistence=0.5,
        confidence=0.9,
    )

    assert assessment.level == SystemicLevel.LOCAL
    assert assessment.is_systemic is False


def test_systemic_change_engine_identifies_no_systemic_significance():
    state_change = make_material_state_change()

    engine = SystemicChangeEngine()

    assessment = engine.assess(
        change_id="SYSTEMIC-003",
        state_change=state_change,
        assessed_at=datetime.now(timezone.utc),
        scope=0.0,
        dependency_relevance=0.0,
        cross_domain_relevance=0.0,
        persistence=0.1,
        confidence=0.5,
    )

    assert assessment.level == SystemicLevel.NONE
    assert assessment.is_systemic is False


@pytest.mark.parametrize(
    "field",
    [
        "scope",
        "dependency_relevance",
        "cross_domain_relevance",
        "persistence",
        "confidence",
    ],
)
def test_systemic_change_engine_validates_scores(field):
    state_change = make_material_state_change()

    engine = SystemicChangeEngine()

    values = {
        "scope": 0.5,
        "dependency_relevance": 0.5,
        "cross_domain_relevance": 0.5,
        "persistence": 0.5,
        "confidence": 0.5,
    }

    values[field] = 1.1

    with pytest.raises(ValueError):
        engine.assess(
            change_id="SYSTEMIC-004",
            state_change=state_change,
            assessed_at=datetime.now(timezone.utc),
            **values,
        )


def test_systemic_change_assessment_preserves_state_change_chain():
    state_change = make_material_state_change()

    engine = SystemicChangeEngine()

    assessment = engine.assess(
        change_id="SYSTEMIC-005",
        state_change=state_change,
        assessed_at=datetime.now(timezone.utc),
        scope=0.8,
        dependency_relevance=0.8,
        cross_domain_relevance=0.8,
        persistence=0.8,
        confidence=0.9,
    )

    assert assessment.state_change is state_change
    assert assessment.state_change.state_diff.changed is True
    assert assessment.state_change.affected_paths == [
        "facility_A.status"
    ]