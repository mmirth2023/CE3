from ce3.statespace import (
    StateSpaceDiff,
    StateSpaceDimension,
    StateSpaceEngine,
    StateSpacePosition,
    StateSpaceSequenceEngine,
    StateSpaceTransition,
    StateSpaceTransitionEngine,
    StateSpaceTransitionHistory,
    StateSpaceTransitionSequence,
    StateSpaceTransitionSequenceHistory,
    StateSpaceTransitionType,
)


def test_statespace_public_api_exports_core_components():
    assert StateSpaceDiff is not None
    assert StateSpaceDimension is not None
    assert StateSpaceEngine is not None
    assert StateSpacePosition is not None


def test_statespace_public_api_exports_transition_components():
    assert StateSpaceTransition is not None
    assert StateSpaceTransitionEngine is not None
    assert StateSpaceTransitionHistory is not None
    assert StateSpaceTransitionType is not None


def test_statespace_public_api_exports_sequence_components():
    assert StateSpaceTransitionSequence is not None
    assert StateSpaceSequenceEngine is not None
    assert StateSpaceTransitionSequenceHistory is not None


def test_sequence_engine_is_publicly_constructible():
    engine = StateSpaceSequenceEngine()

    assert isinstance(
        engine,
        StateSpaceSequenceEngine,
    )


def test_sequence_history_is_publicly_constructible():
    history = StateSpaceTransitionSequenceHistory()

    assert isinstance(
        history,
        StateSpaceTransitionSequenceHistory,
    )