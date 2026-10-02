from datetime import datetime, timezone

from ce3.temporal.timestamps import TemporalTimestamps


def test_temporal_timestamps_preserve_distinct_clocks():
    event_time = datetime(
        2026, 10, 2, 15, 0, 0,
        tzinfo=timezone.utc,
    )

    published_time = datetime(
        2026, 10, 2, 15, 0, 10,
        tzinfo=timezone.utc,
    )

    observed_time = datetime(
        2026, 10, 2, 15, 0, 12,
        tzinfo=timezone.utc,
    )

    ingested_time = datetime(
        2026, 10, 2, 15, 0, 15,
        tzinfo=timezone.utc,
    )

    state_time = datetime(
        2026, 10, 2, 15, 0, 17,
        tzinfo=timezone.utc,
    )

    timestamps = TemporalTimestamps(
        event_time=event_time,
        published_time=published_time,
        observed_time=observed_time,
        ingested_time=ingested_time,
        state_time=state_time,
    )

    assert timestamps.event_time == event_time
    assert timestamps.published_time == published_time
    assert timestamps.observed_time == observed_time
    assert timestamps.ingested_time == ingested_time
    assert timestamps.state_time == state_time


def test_information_latency_is_calculated_from_event_to_ingestion():
    timestamps = TemporalTimestamps(
        event_time=datetime(
            2026, 10, 2, 15, 0, 0,
            tzinfo=timezone.utc,
        ),
        observed_time=datetime(
            2026, 10, 2, 15, 0, 5,
            tzinfo=timezone.utc,
        ),
        ingested_time=datetime(
            2026, 10, 2, 15, 0, 12,
            tzinfo=timezone.utc,
        ),
    )

    assert timestamps.information_latency_seconds == 12.0


def test_publication_latency_is_calculated_from_publication_to_ingestion():
    timestamps = TemporalTimestamps(
        published_time=datetime(
            2026, 10, 2, 15, 0, 10,
            tzinfo=timezone.utc,
        ),
        observed_time=datetime(
            2026, 10, 2, 15, 0, 11,
            tzinfo=timezone.utc,
        ),
        ingested_time=datetime(
            2026, 10, 2, 15, 0, 15,
            tzinfo=timezone.utc,
        ),
    )

    assert timestamps.publication_latency_seconds == 5.0


def test_latency_is_none_when_event_time_is_unknown():
    timestamps = TemporalTimestamps(
        observed_time=datetime(
            2026, 10, 2, 15, 0, 5,
            tzinfo=timezone.utc,
        ),
        ingested_time=datetime(
            2026, 10, 2, 15, 0, 12,
            tzinfo=timezone.utc,
        ),
    )

    assert timestamps.information_latency_seconds is None