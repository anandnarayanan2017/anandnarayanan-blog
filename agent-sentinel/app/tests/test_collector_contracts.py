from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from sentinel.api.main import FlowIn
from sentinel.collector.anthropic_sdk import _AsyncMessagesSentinel, _MessagesSentinel
from sentinel.collector.azure_openai import (
    _AsyncCompletionsSentinel,
    _ChatSentinel,
    _CompletionsSentinel,
)
from sentinel.collector.parsers import parse_flow
from sentinel.collector.redaction import redact_text
from sentinel.collector.sdk_base import MAX_REQUEST_CHARS, SentinelReporter, bound_request
from sentinel.detection.engine import Engine
from sentinel.detection.policy import PolicySet
from sentinel.schema.events import ActionType


def test_redaction_removes_sensitive_json_fields_and_common_identifiers():
    raw = json.dumps(
        {
            "api_key": "sk-abcdefghijklmnopqrstuvwxyz",
            "message": "email alice@example.com IBAN LU280019400644750000",
        }
    )
    result = redact_text(raw)
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in result
    assert "alice@example.com" not in result
    assert "LU280019400644750000" not in result
    assert result.count("[REDACTED]") >= 3


def test_reporter_sends_bearer_token_and_redacts_before_transport(monkeypatch):
    captured = {}

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"findings":0}'

    def _urlopen(req, timeout):
        captured["authorization"] = req.get_header("Authorization")
        captured["payload"] = json.loads(req.data.decode())
        return _Response()

    monkeypatch.setattr("urllib.request.urlopen", _urlopen)
    reporter = SentinelReporter("agent-1", "session-1", auth_token="token-value")
    reporter.report(host="api.openai.com", request_body='{"password":"secret"}')

    assert captured["authorization"] == "Bearer token-value"
    assert "secret" not in captured["payload"]["request_body"]


def test_model_proposal_is_tool_requested_not_executed(monkeypatch):
    captured = {}
    reporter = SentinelReporter("agent-1", "session-1")

    def _capture(**kwargs):
        captured.update(kwargs)
        return {}

    monkeypatch.setattr(reporter, "report", _capture)
    reporter.report_tool_request(host="api.openai.com", tool_name="wire_transfer", args={})
    event = parse_flow(
        agent_id="agent-1",
        session_id="session-1",
        host="api.openai.com",
        method="POST",
        path=captured["path"],
        request_body=captured["request_body"],
    )
    assert event.action == ActionType.TOOL_REQUESTED


def test_tool_policy_does_not_treat_requested_tool_as_executed(tmp_path):
    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text(
        "agents:\n  - agent_id: agent-1\n    allowed_tools: [safe_tool]\n",
        encoding="utf-8",
    )
    engine = Engine(PolicySet.from_yaml(policy_path))
    event = parse_flow(
        agent_id="agent-1",
        session_id="session-1",
        host="api.openai.com",
        method="POST",
        path="/model/tool-requested",
        request_body=json.dumps(
            {"jsonrpc": "2.0", "method": "tools/requested", "params": {"name": "dangerous"}}
        ),
    )
    assert not [
        finding for finding in engine.evaluate(event) if finding.rule_id == "tool.not_allowed"
    ]


def test_async_azure_wrapper_exposes_awaitable_create(monkeypatch):
    class _Completions:
        async def create(self, **kwargs):
            return SimpleNamespace(
                choices=[], model_dump_json=lambda: json.dumps({"model": kwargs["model"]})
            )

    reports = []
    reporter = SentinelReporter("agent-1", "session-1")
    monkeypatch.setattr(reporter, "report", lambda **kwargs: reports.append(kwargs) or {})
    wrapper = _AsyncCompletionsSentinel(_Completions(), reporter, "azure.example")

    response = asyncio.run(wrapper.create(model="gpt-4o", messages=[]))
    assert response is not None
    assert len(reports) == 1


def test_async_anthropic_wrapper_exposes_awaitable_create(monkeypatch):
    class _Messages:
        async def create(self, **kwargs):
            return SimpleNamespace(
                content=[], model_dump_json=lambda: json.dumps({"model": kwargs["model"]})
            )

    reports = []
    reporter = SentinelReporter("agent-1", "session-1")
    monkeypatch.setattr(reporter, "report", lambda **kwargs: reports.append(kwargs) or {})
    wrapper = _AsyncMessagesSentinel(_Messages(), reporter)

    response = asyncio.run(wrapper.create(model="claude", messages=[], max_tokens=32))
    assert response is not None
    assert len(reports) == 1


# ---- Part 2: gaps found by testing the wrappers against "if the recorder
# fails, the agent must not", one regression test each ------------------------

EXAMPLE_POLICY = Path(__file__).resolve().parents[2] / "policies" / "example.yaml"


def _capturing_reporter(monkeypatch):
    reports = []
    reporter = SentinelReporter("recon-bot", "session-1")
    monkeypatch.setattr(reporter, "report", lambda **kwargs: reports.append(kwargs) or {})
    return reporter, reports


def _ok_response():
    return SimpleNamespace(content=[], choices=[], model_dump_json=lambda: "{}")


def test_unwrapped_sdk_methods_pass_through_instead_of_breaking_the_agent(monkeypatch):
    """messages.stream / count_tokens / batches used to raise AttributeError."""
    reporter, _ = _capturing_reporter(monkeypatch)
    real_messages = SimpleNamespace(
        create=lambda **kw: _ok_response(),
        stream=lambda **kw: "stream-handle",
        count_tokens=lambda **kw: 42,
        batches="batches-api",
    )
    wrapped = _MessagesSentinel(real_messages, reporter)
    assert wrapped.stream(model="m") == "stream-handle"
    assert wrapped.count_tokens(model="m") == 42
    assert wrapped.batches == "batches-api"
    assert _AsyncMessagesSentinel(real_messages, reporter).count_tokens() == 42

    real_chat = SimpleNamespace(
        completions=SimpleNamespace(create=lambda **kw: _ok_response(), parse=lambda **kw: "p"),
        other="chat-attr",
    )
    chat = _ChatSentinel(real_chat, reporter, "azure.example")
    assert chat.completions.parse() == "p"
    assert chat.other == "chat-attr"
    with pytest.raises(AttributeError):
        _ = wrapped.no_such_method  # a real typo still fails loudly


def test_long_prompt_keeps_model_and_real_size_so_rules_still_fire(monkeypatch):
    """Over 8KB the JSON used to be cut mid-text: no model, size capped at 8192,
    so model.not_allowed and the oversize rule could not fire."""
    reporter, reports = _capturing_reporter(monkeypatch)
    real_messages = SimpleNamespace(create=lambda **kw: _ok_response())
    big = [{"role": "user", "content": "ledger row\n" * 15_000}]  # ~165KB
    _MessagesSentinel(real_messages, reporter).create(
        model="claude-unapproved", messages=big, max_tokens=64
    )
    sent = reports[0]
    assert len(sent["request_body"]) <= MAX_REQUEST_CHARS
    assert sent["request_bytes"] > 150_000

    # Through the server's request model, exactly as POST /ingest receives it.
    flow = FlowIn(
        agent_id="recon-bot",
        session_id="session-1",
        host=sent["host"],
        path=sent["path"],
        request_body=sent["request_body"],
        request_bytes=sent["request_bytes"],
    )
    event = parse_flow(**flow.model_dump())
    assert event.model == "claude-unapproved"
    assert event.bytes_out == sent["request_bytes"]
    assert event.attributes["request_truncated"] is True
    assert event.attributes["message_count"] == 1

    rules = {f.rule_id for f in Engine(PolicySet.from_yaml(EXAMPLE_POLICY)).evaluate(event)}
    assert "model.not_allowed" in rules
    assert "net.oversize_egress" in rules


def test_bounded_preview_is_redacted_before_it_is_cut():
    """A secret straddling the preview's cut must not leave its first digits behind."""
    card = "4111111111111111"
    cut = MAX_REQUEST_CHARS // 4
    pad = "x " * ((cut - 30) // 2)
    messages = [{"role": "user", "content": pad + card + " " + "y" * MAX_REQUEST_CHARS}]
    body, _ = bound_request("m", messages, {})
    assert "41111111" not in body
    assert json.loads(body)["model"] == "m"


def test_short_requests_are_sent_whole():
    body, size = bound_request("m", [{"role": "user", "content": "hi"}], {"max_tokens": 5})
    assert json.loads(body) == {
        "model": "m",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5,
    }
    assert size == len(body.encode())


def test_provider_errors_are_recorded_and_reraised_unchanged(monkeypatch):
    class _Overloaded(Exception):
        status_code = 529

    def _fail(**kw):
        raise _Overloaded("overloaded")

    reporter, reports = _capturing_reporter(monkeypatch)
    with pytest.raises(_Overloaded):
        _MessagesSentinel(SimpleNamespace(create=_fail), reporter).create(
            model="m", messages=[], max_tokens=1
        )
    with pytest.raises(_Overloaded):
        _CompletionsSentinel(SimpleNamespace(create=_fail), reporter, "azure.example").create(
            model="m", messages=[]
        )

    async def _afail(**kw):
        raise _Overloaded("overloaded")

    with pytest.raises(_Overloaded):
        asyncio.run(
            _AsyncMessagesSentinel(SimpleNamespace(create=_afail), reporter).create(
                model="m", messages=[], max_tokens=1
            )
        )
    assert [r["status_code"] for r in reports] == [529, 529, 529]
    assert all(json.loads(r["response_body"]) == {"error": "_Overloaded"} for r in reports)


def test_delivery_failures_are_counted_not_only_logged():
    reporter = SentinelReporter("agent-1", "session-1", sentinel_api="http://127.0.0.1:1")
    assert reporter.report(host="api.anthropic.com") == {}
    assert reporter.report(host="api.anthropic.com") == {}
    assert reporter.delivery_failures == 2


def test_async_reporting_does_not_block_the_event_loop(monkeypatch):
    """A slow Sentinel used to freeze every other coroutine in the agent."""
    reporter = SentinelReporter("agent-1", "session-1")
    monkeypatch.setattr(reporter, "report", lambda **kw: time.sleep(0.3) or {})

    class _Messages:
        async def create(self, **kwargs):
            return _ok_response()

    async def _scenario():
        finished = []

        async def _ticker():
            for _ in range(10):
                await asyncio.sleep(0.01)
            finished.append("ticker")

        async def _call():
            await _AsyncMessagesSentinel(_Messages(), reporter).create(
                model="m", messages=[], max_tokens=1
            )
            finished.append("model call")

        await asyncio.gather(_call(), _ticker())
        return finished

    # Blocking the loop for the 0.3s report would let the model call finish
    # before the 0.1s ticker; reporting off the loop lets the ticker finish first.
    assert asyncio.run(_scenario()) == ["ticker", "model call"]
