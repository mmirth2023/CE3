from datetime import datetime, timezone

from ce3.state.models import ControlStatus
from ce3.state.transitions import StateTransition


def test_state_transition_can_be_created():
    occurred_at = datetime.now(timezone.utc)

    transition = StateTransition(
        conflict_id="C1",
        entity="Facility X",
        dimension="territorial",
        occurred_at=occurred_at,
        previous_value=ControlStatus.CONTROLLED,
        new_value=ControlStatus.CONTESTED,
        source_event_id="E2",
    )

    assert transition.conflict_id == "C1"
    assert transition.entity == "Facility X"
    assert transition.dimension == "territorial"
    assert transition.previous_value == ControlStatus.CONTROLLED
    assert transition.new_value == ControlStatus.CONTESTED
    assert transition.source_event_id == "E2"