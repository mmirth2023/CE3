from datetime import datetime, timezone

from ce3.temporal.observation import TemporalObservation
from ce3.temporal.timestamps import TemporalTimestamps


def test_temporal_observation_preserves_content_and_temporal_metadata():
    event_time = datetime(
        2026, 10, 2, 15, 0, 0,
        tzinfo=timezone.utc,
    )

    observed_time = datetime(
        2026, 10, 2, 15, 0, 5,
        tzinfo=timezone.utc,
    )

    ingested_time = datetime(
        2026, 10, 2, 15, 0, 8,
        tzinfo=timezone.utc,
    )

    observation = TemporalObservation(
        id="OBS-001",
        source_id="SAT-001",
        timestamps=TemporalTimestamps(
            event_time=event_time,
            observed_time=observed_time,
            ingested_time=ingested_time,
        ),
        content="Satellite imagery shows smoke near Facility X.",
        entities=["facility_x"],
    )

    assert observation.id == "OBS-001"
    assert observation.source_id == "SAT-001"
    assert observation.content == (
        "Satellite imagery shows smoke near Facility X."
    )
    assert observation.entities == ["facility_x"]
    assert observation.timestamps.event_time == event_time


def test_temporal_observation_supports_multiple_entities():
    timestamps = TemporalTimestamps(
        observed_time=datetime(
            2026, 10, 2, 15, 0, 5,
            tzinfo=timezone.utc,
        ),
        ingested_time=datetime(
            2026, 10, 2, 15, 0, 8,
            tzinfo=timezone.utc,
        ),
    )

    observation = TemporalObservation(
        id="OBS-002",
        source_id="NEWS-001",
        timestamps=timestamps,
        content="Company A suspended exports through Port B.",
        entities=["company_a", "port_b"],
    )

    assert observation.entities == [
        "company_a",
        "port_b",
    ]


def test_temporal_observation_defaults_are_safe():
    timestamps = TemporalTimestamps(
        observed_time=datetime(
            2026, 10, 2, 15, 0, 5,
            tzinfo=timezone.utc,
        ),
        ingested_time=datetime(
            2026, 10, 2, 15, 0, 8,
            tzinfo=timezone.utc,
        ),
    )

    observation = TemporalObservation(
        id="OBS-003",
        source_id="SRC-001",
        timestamps=timestamps,
        content="Observation content.",
    )

    assert observation.entities == []
    assert observation.metadata == {}