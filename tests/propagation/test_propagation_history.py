from datetime import datetime, timezone

import pytest

from ce3.propagation import (
    PropagationHistory,
    PropagationPath,
    PropagationStatus,
    PropagationType,
)


def make_path(
    path_id: str,
    identified_at: datetime,
    source_id: str = "entity_A",
    target_id: str = "entity_B",
) -> PropagationPath:
    return PropagationPath(
        id=path_id,
        source_id=source_id,
        target_id=target_id,
        propagation_type=PropagationType.DEPENDENCY,
        status=PropagationStatus.SUPPORTED,
        identified_at=identified_at,
        strength=0.8,
        confidence=0.9,
    )


def test_history_adds_and_retrieves_paths():
    history = PropagationHistory()

    path = make_path(
        "PROP-001",
        datetime(
            2026,
            10,
            3,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    history.add(path)

    assert history.get("PROP-001") is path
    assert len(history) == 1


def test_history_rejects_duplicate_ids():
    history = PropagationHistory()

    timestamp = datetime(
        2026,
        10,
        3,
        10,
        0,
        tzinfo=timezone.utc,
    )

    history.add(make_path("PROP-001", timestamp))

    with pytest.raises(ValueError):
        history.add(make_path("PROP-001", timestamp))


def test_history_preserves_chronological_order():
    history = PropagationHistory()

    later = datetime(
        2026,
        10,
        3,
        12,
        0,
        tzinfo=timezone.utc,
    )

    earlier = datetime(
        2026,
        10,
        3,
        10,
        0,
        tzinfo=timezone.utc,
    )

    history.add(make_path("PROP-002", later))
    history.add(make_path("PROP-001", earlier))

    assert [
        path.id
        for path in history.all()
    ] == [
        "PROP-001",
        "PROP-002",
    ]


def test_history_between_is_inclusive():
    history = PropagationHistory()

    first = datetime(
        2026,
        10,
        3,
        10,
        0,
        tzinfo=timezone.utc,
    )

    second = datetime(
        2026,
        10,
        3,
        11,
        0,
        tzinfo=timezone.utc,
    )

    third = datetime(
        2026,
        10,
        3,
        12,
        0,
        tzinfo=timezone.utc,
    )

    history.add(make_path("PROP-001", first))
    history.add(make_path("PROP-002", second))
    history.add(make_path("PROP-003", third))

    result = history.between(first, second)

    assert [
        path.id
        for path in result
    ] == [
        "PROP-001",
        "PROP-002",
    ]


def test_history_rejects_invalid_between_range():
    history = PropagationHistory()

    start = datetime(
        2026,
        10,
        3,
        12,
        0,
        tzinfo=timezone.utc,
    )

    end = datetime(
        2026,
        10,
        3,
        10,
        0,
        tzinfo=timezone.utc,
    )

    with pytest.raises(ValueError):
        history.between(start, end)


def test_history_as_of_and_latest():
    history = PropagationHistory()

    first = datetime(
        2026,
        10,
        3,
        10,
        0,
        tzinfo=timezone.utc,
    )

    second = datetime(
        2026,
        10,
        3,
        11,
        0,
        tzinfo=timezone.utc,
    )

    third = datetime(
        2026,
        10,
        3,
        12,
        0,
        tzinfo=timezone.utc,
    )

    history.add(make_path("PROP-001", first))
    history.add(make_path("PROP-002", second))
    history.add(make_path("PROP-003", third))

    assert [
        path.id
        for path in history.as_of(second)
    ] == [
        "PROP-001",
        "PROP-002",
    ]

    assert history.latest(second).id == "PROP-002"
    assert history.latest().id == "PROP-003"


def test_history_valid_at():
    history = PropagationHistory()

    path = PropagationPath(
        id="PROP-001",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.SUPPLY,
        identified_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        valid_from=datetime(
            2026,
            2,
            1,
            tzinfo=timezone.utc,
        ),
        valid_to=datetime(
            2026,
            12,
            31,
            tzinfo=timezone.utc,
        ),
    )

    history.add(path)

    assert history.valid_at(
        datetime(
            2026,
            6,
            1,
            tzinfo=timezone.utc,
        )
    ) == [path]

    assert history.valid_at(
        datetime(
            2027,
            1,
            1,
            tzinfo=timezone.utc,
        )
    ) == []


def test_history_filters_by_source_and_target():
    history = PropagationHistory()

    history.add(
        make_path(
            "PROP-001",
            datetime(
                2026,
                10,
                3,
                10,
                0,
                tzinfo=timezone.utc,
            ),
            source_id="entity_A",
            target_id="entity_B",
        )
    )

    history.add(
        make_path(
            "PROP-002",
            datetime(
                2026,
                10,
                3,
                11,
                0,
                tzinfo=timezone.utc,
            ),
            source_id="entity_C",
            target_id="entity_B",
        )
    )

    assert [
        path.id
        for path in history.from_source("entity_A")
    ] == ["PROP-001"]

    assert [
        path.id
        for path in history.to_target("entity_B")
    ] == [
        "PROP-001",
        "PROP-002",
    ]


def test_history_between_nodes():
    history = PropagationHistory()

    path = make_path(
        "PROP-001",
        datetime(
            2026,
            10,
            3,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        source_id="entity_A",
        target_id="entity_B",
    )

    history.add(path)

    assert history.between_nodes(
        "entity_A",
        "entity_B",
    ) == [path]

    assert history.between_nodes(
        "entity_B",
        "entity_A",
    ) == []


def test_history_affecting_includes_intermediate_nodes():
    history = PropagationHistory()

    path = PropagationPath(
        id="PROP-001",
        source_id="entity_A",
        target_id="entity_C",
        propagation_type=PropagationType.SUPPLY,
        identified_at=datetime.now(timezone.utc),
        intermediate_ids=[
            "entity_B",
        ],
    )

    history.add(path)

    assert history.affecting("entity_A") == [path]
    assert history.affecting("entity_B") == [path]
    assert history.affecting("entity_C") == [path]
    assert history.affecting("entity_D") == []


def test_history_filters_relationship_and_dependency():
    history = PropagationHistory()

    path_one = PropagationPath(
        id="PROP-001",
        source_id="entity_A",
        target_id="entity_B",
        propagation_type=PropagationType.DEPENDENCY,
        identified_at=datetime.now(timezone.utc),
        relationship_id="REL-001",
        dependency_id="DEP-001",
    )

    path_two = PropagationPath(
        id="PROP-002",
        source_id="entity_B",
        target_id="entity_C",
        propagation_type=PropagationType.SUPPLY,
        identified_at=datetime.now(timezone.utc),
        relationship_id="REL-002",
        dependency_id="DEP-002",
    )

    history.add(path_one)
    history.add(path_two)

    assert history.by_relationship("REL-001") == [path_one]
    assert history.by_dependency("DEP-002") == [path_two]


def test_empty_history_queries_are_safe():
    history = PropagationHistory()

    timestamp = datetime.now(timezone.utc)

    assert history.all() == []
    assert history.latest() is None
    assert history.as_of(timestamp) == []
    assert history.between(timestamp, timestamp) == []
    assert history.valid_at(timestamp) == []
    assert history.from_source("entity_A") == []
    assert history.to_target("entity_B") == []
    assert history.between_nodes(
        "entity_A",
        "entity_B",
    ) == []
    assert history.affecting("entity_A") == []