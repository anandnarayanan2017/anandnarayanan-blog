"""Anthropic SDK interceptor — Phase 2 collector.

Drop-in replacement for ``anthropic.Anthropic``.  Every messages.create() call
and embedded tool_use block is reported to Sentinel automatically, including
calls the provider rejects. Anything not wrapped here (``messages.stream``,
``count_tokens``, batches) is passed through to the real client unrecorded.

Install:
    pip install "agent-sentinel[anthropic]"

Usage::

    from sentinel.collector.anthropic_sdk import AnthropicSentinel

    client = AnthropicSentinel(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        # Sentinel kwargs:
        agent_id="kyc-agent",
        session_id="sess-20240601",
        sentinel_api="http://localhost:8000",
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": "Verify identity for customer #8821."}],
    )
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from sentinel.collector.sdk_base import SentinelReporter, bound_request

_ANTHROPIC_HOST = "api.anthropic.com"
_PATH = "/v1/messages"


# ── Proxy wrappers ────────────────────────────────────────────────────────────


class _MessagesSentinel:
    """Intercepts messages.create(). Everything else is passed through.

    ``stream``, ``count_tokens``, ``batches`` and any later SDK addition reach
    the real client unchanged (and unrecorded): a wrapper that raises
    AttributeError for methods it doesn't know breaks the agent it watches.
    """

    def __init__(self, messages: Any, reporter: SentinelReporter) -> None:
        self._messages = messages
        self._rep = reporter

    def __getattr__(self, name: str) -> Any:
        return getattr(self._messages, name)

    def create(self, *, model: str, messages: list[dict], max_tokens: int, **kwargs: Any) -> Any:
        body, size = _serialise_request(model, messages, max_tokens, kwargs)
        try:
            response = self._messages.create(
                model=model, messages=messages, max_tokens=max_tokens, **kwargs
            )
        except Exception as exc:
            _record_error(self._rep, body, size, exc)
            raise
        _record(self._rep, body, size, response)
        return response


class _AsyncMessagesSentinel:
    """Async SDK surface: callers use ``await client.messages.create``.

    Reporting runs in a worker thread, so a slow Sentinel delays this call by at
    most the reporter's timeout and never blocks the agent's event loop.
    """

    def __init__(self, messages: Any, reporter: SentinelReporter) -> None:
        self._messages = messages
        self._rep = reporter

    def __getattr__(self, name: str) -> Any:
        return getattr(self._messages, name)

    async def create(
        self, *, model: str, messages: list[dict], max_tokens: int, **kwargs: Any
    ) -> Any:
        body, size = _serialise_request(model, messages, max_tokens, kwargs)
        try:
            response = await self._messages.create(
                model=model, messages=messages, max_tokens=max_tokens, **kwargs
            )
        except Exception as exc:
            await asyncio.to_thread(_record_error, self._rep, body, size, exc)
            raise
        await asyncio.to_thread(_record, self._rep, body, size, response)
        return response

    acreate = create


# ── Public wrapper ────────────────────────────────────────────────────────────


class AnthropicSentinel:
    """Wraps Anthropic messages.create() and reports covered calls to Sentinel.

    Sentinel-specific identity, endpoint, and auth-token kwargs are consumed by
    this wrapper; remaining kwargs are forwarded to ``anthropic.Anthropic``.
    """

    def __init__(
        self,
        *,
        agent_id: str,
        session_id: str = "default",
        sentinel_api: str = "http://localhost:8000",
        sentinel_auth_token: str | None = None,
        sentinel_token_provider: Any = None,
        **anthropic_kwargs: Any,
    ) -> None:
        try:
            # anthropic is an optional extra (`pip install 'agent-sentinel[anthropic]'`);
            # this lazy import is the documented seam that keeps it out of core
            # deps, so a missing-in-this-env import is expected, not a code bug.
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "Install the Anthropic extra:  pip install 'agent-sentinel[anthropic]'"
            ) from exc

        self._client = anthropic.Anthropic(**anthropic_kwargs)
        self._reporter = SentinelReporter(
            agent_id=agent_id,
            session_id=session_id,
            sentinel_api=sentinel_api,
            auth_token=sentinel_auth_token,
            token_provider=sentinel_token_provider,
        )
        self.messages = _MessagesSentinel(self._client.messages, self._reporter)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


class AsyncAnthropicSentinel:
    """Async variant — wraps ``anthropic.AsyncAnthropic``."""

    def __init__(
        self,
        *,
        agent_id: str,
        session_id: str = "default",
        sentinel_api: str = "http://localhost:8000",
        sentinel_auth_token: str | None = None,
        sentinel_token_provider: Any = None,
        **anthropic_kwargs: Any,
    ) -> None:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "Install the Anthropic extra:  pip install 'agent-sentinel[anthropic]'"
            ) from exc

        self._client = anthropic.AsyncAnthropic(**anthropic_kwargs)
        self._reporter = SentinelReporter(
            agent_id=agent_id,
            session_id=session_id,
            sentinel_api=sentinel_api,
            auth_token=sentinel_auth_token,
            token_provider=sentinel_token_provider,
        )
        self.messages = _AsyncMessagesSentinel(self._client.messages, self._reporter)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _serialise_request(
    model: str, messages: list, max_tokens: int, kwargs: dict
) -> tuple[str, int]:
    return bound_request(model, messages, {"max_tokens": max_tokens, **kwargs})


def _serialise_response(response: Any) -> str:
    try:
        return response.model_dump_json()[:4096]
    except Exception:  # noqa: BLE001 — any SDK response shape; telemetry must never raise into the agent
        return str(response)[:4096]


def _record(reporter: SentinelReporter, body: str, size: int, response: Any) -> None:
    reporter.report(
        host=_ANTHROPIC_HOST,
        method="POST",
        path=_PATH,
        request_body=body,
        request_bytes=size,
        response_body=_serialise_response(response),
        status_code=200,
    )
    _report_tool_use(response, reporter)


def _record_error(reporter: SentinelReporter, body: str, size: int, exc: Exception) -> None:
    """Record a call the provider rejected; the caller re-raises the error unchanged."""
    reporter.report(
        host=_ANTHROPIC_HOST,
        method="POST",
        path=_PATH,
        request_body=body,
        request_bytes=size,
        response_body=json.dumps({"error": type(exc).__name__}),
        status_code=getattr(exc, "status_code", None),
    )


def _report_tool_use(response: Any, reporter: SentinelReporter) -> None:
    """Report Anthropic tool_use blocks as requested, not executed, tools."""
    try:
        for block in response.content:
            if getattr(block, "type", None) == "tool_use":
                reporter.report_tool_request(
                    host=_ANTHROPIC_HOST,
                    tool_name=block.name,
                    args=block.input if isinstance(block.input, dict) else {},
                )
    except Exception:  # noqa: BLE001, S110 — telemetry must never raise into the agent
        pass
