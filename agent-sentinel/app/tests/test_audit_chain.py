"""The audit hash chain: what `verify_chain` detects, and the one thing it cannot.

`storage/audit_chain.py` is pure (no database), so these tests build a chain
the way `PGStore.insert_audit` does and then tamper with it.
"""

import copy

from sentinel.storage.audit_chain import GENESIS_HASH, entry_hash, verify_chain


def _chain(n=5):
    rows, prev = [], GENESIS_HASH
    for i in range(n):
        row = {
            "audit_id": f"a{i}",
            "ts": f"2026-11-16T09:00:0{i}+00:00",
            "endpoint": "/findings",
            "method": "GET",
            "agent_id": None,
            "source_ip": "10.0.0.7",
            "payload_hash": None,
            "status_code": 200,
            "duration_ms": 3 + i,
            "user_id": "analyst-1",
        }
        row["prev_hash"] = prev
        row["entry_hash"] = prev = entry_hash(prev, row)
        rows.append(row)
    return rows


def test_untouched_chain_verifies():
    assert verify_chain(_chain()) is None


def test_empty_log_verifies():
    assert verify_chain([]) is None


def test_edited_entry_is_named():
    rows = _chain()
    rows[2]["user_id"] = "someone-else"  # rewrite who made the request

    broken = verify_chain(rows)

    assert broken["index"] == 2
    assert broken["audit_id"] == "a2"
    assert broken["reason"] == "entry_hash does not match this entry's content"


def test_deleted_entry_breaks_the_next_link():
    rows = _chain()
    del rows[2]

    broken = verify_chain(rows)

    assert broken["index"] == 2  # the row that now follows the gap
    assert broken["audit_id"] == "a3"
    assert broken["reason"] == "prev_hash does not match the preceding entry"


def test_reordered_entries_are_detected():
    rows = _chain()
    rows[1], rows[2] = rows[2], rows[1]

    assert verify_chain(rows)["index"] == 1


def test_removed_oldest_entries_are_detected():
    broken = verify_chain(_chain()[2:])

    assert broken["index"] == 0
    assert "genesis" in broken["reason"]


def test_removed_newest_entries_are_not_detected_without_an_outside_anchor():
    """Cutting the end of the log leaves a shorter chain that still verifies.

    Only the stored chain head (`audit_chain.last_hash`), or a copy of it kept
    outside the database, shows that entries are missing.
    """
    assert verify_chain(_chain()[:3]) is None


def test_a_full_rewrite_is_not_detected_without_an_outside_anchor():
    """Someone who can rewrite every later row can rebuild a valid chain."""
    rows = copy.deepcopy(_chain())
    rows[2]["user_id"] = "someone-else"
    prev = rows[1]["entry_hash"]
    for row in rows[2:]:
        row["prev_hash"] = prev
        row["entry_hash"] = prev = entry_hash(prev, row)

    assert verify_chain(rows) is None
