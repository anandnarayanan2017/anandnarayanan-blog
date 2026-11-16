"""What the storage layer promises the recorder, and what it does not keep.

These back the data-platform write-up: an event is stored before it is judged,
re-sent events do not duplicate, and only part of the detection state survives
a restart.
"""

from pathlib import Path

import pytest
from sentinel.collector.parsers import parse_flow
from sentinel.detection.baseline import BaselineStore
from sentinel.pipeline import Pipeline
from sentinel.storage.store import Store

POLICY = str(Path(__file__).resolve().parents[1].parent / "policies" / "example.yaml")


def _flow(**kw):
    base = {
        "agent_id": "recon-bot",
        "session_id": "s",
        "host": "ledger.internal",
        "method": "POST",
        "path": "/t",
    }
    return {**base, **kw}


def test_event_is_stored_before_it_is_evaluated(monkeypatch):
    """If detection fails, the record of what the agent did is already kept."""
    pipe = Pipeline(POLICY, ":memory:")

    def boom(_event):
        raise RuntimeError("detection bug")

    monkeypatch.setattr(pipe.engine, "evaluate", boom)

    with pytest.raises(RuntimeError):
        pipe.ingest_flow(**_flow(request_body="x"))

    assert len(pipe.store.events_for_agent("recon-bot")) == 1


def test_resending_the_same_event_does_not_duplicate_it():
    store = Store(":memory:")
    event = parse_flow(**_flow(request_body="x"))

    store.insert_event(event)
    store.insert_event(event)  # a collector retry

    assert store.stats()["total_events"] == 1


def test_known_hosts_are_rebuilt_from_the_store_after_a_restart():
    store = Store(":memory:")
    store.insert_event(parse_flow(**_flow(host="ledger.internal")))
    store.insert_event(parse_flow(**_flow(host="reports.internal")))

    restarted = BaselineStore(store)  # a new process: empty memory, same store

    assert restarted.get("recon-bot").seen_hosts == {"ledger.internal", "reports.internal"}


def test_payload_history_is_not_rebuilt_after_a_restart():
    """Payload-size samples live in memory only, so the size baseline starts cold."""
    store = Store(":memory:")
    for size in (100, 120, 140, 160, 180, 200):
        store.insert_event(parse_flow(**_flow(request_body="x" * size)))

    restarted = BaselineStore(store)

    assert len(restarted.get("recon-bot").bytes_out_samples) == 0
    assert restarted.get("recon-bot").bytes_out_z(60_000) == 0.0


def test_evidence_preview_is_bounded_and_the_real_size_is_kept():
    """A 50 KB body is stored as a 256-character preview plus its true size."""
    store = Store(":memory:")
    store.insert_event(parse_flow(**_flow(request_body="A" * 50_000)))

    event = store.list_events(1)[0]
    preview = next(e["value"] for e in event["evidence"] if e["key"] == "body_preview")

    assert len(preview) == 256
    assert event["bytes_out"] == 50_000
