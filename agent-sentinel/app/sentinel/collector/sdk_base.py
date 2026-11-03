"""Base reporter shared by all SDK-level interceptors.

Every SDK wrapper (Azure OpenAI, Anthropic, …) holds a SentinelReporter and
calls .report() after each intercepted call.  Failures never raise into the
agent it is protecting (fail-open), but they are logged and counted in
``delivery_failures`` so a gap in the record stays visible.

The reporter serialises events in the same FlowIn shape that the HTTP /ingest
endpoint expects, so no new schema is needed.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from sentinel.collector.redaction import redact_text

logger = logging.getLogger("sentinel.collector.sdk")

# Largest request body, in characters, sent to Sentinel for one model call.
MAX_REQUEST_CHARS = 8192


def bound_request(model: str, messages: Any, fields: dict[str, Any]) -> tuple[str, int]:
    """Serialise a model request for telemetry. Returns ``(body, real_size_in_bytes)``.

    The body is always valid JSON that names the model. Cutting the JSON text at
    a fixed length, as this used to do, made any request over the limit
    unparsable: Sentinel then recorded the call without its model and with a
    capped size, so the model allowlist and the oversize rule could not fire on
    a long prompt. Over the limit, the messages are replaced by a redacted,
    bounded preview and the real size travels separately.
    """
    full = json.dumps({"model": model, "messages": messages, **fields}, default=str)
    size = len(full.encode())
    if len(full) <= MAX_REQUEST_CHARS:
        return full, size
    # Redact BEFORE truncating, as parsers._preview does: cutting first can leave
    # the part of a secret the redactor no longer recognises.
    preview = redact_text(json.dumps(messages, default=str))[: MAX_REQUEST_CHARS // 4]
    bounded = {
        "model": model,
        "messages": [{"role": "sentinel_truncated", "content": preview}],
        "message_count": len(messages) if isinstance(messages, list) else None,
        "sentinel_truncated": True,
    }
    return json.dumps(bounded, default=str), size


@dataclass
class SentinelReporter:
    agent_id: str
    session_id: str
    sentinel_api: str = "http://localhost:8000"
    auth_token: str | None = None
    token_provider: Callable[[], str] | None = None
    # Events that could not be delivered. Fail-open must not mean fail-silent.
    delivery_failures: int = field(default=0, init=False)

    def report(
        self,
        *,
        host: str,
        method: str = "POST",
        path: str = "/",
        request_body: str | None = None,
        response_body: str | None = None,
        status_code: int | None = 200,
        request_bytes: int | None = None,
    ) -> dict:
        """POST one event to Sentinel.  Returns the ingest response or {} on error."""
        payload = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "host": host,
            "method": method,
            "path": path,
            # Redact at the collection edge so sensitive values are not sent
            # over the wire to Sentinel in the first place.
            "request_body": redact_text(request_body) if request_body is not None else None,
            "response_body": redact_text(response_body) if response_body is not None else None,
            "status_code": status_code,
        }
        if request_bytes is not None:
            # The real request size, when request_body is a bounded preview.
            payload["request_bytes"] = request_bytes
        try:
            # bandit B310: sentinel_api is a deployment-time constructor arg
            # (operator config), never attacker-controlled — validated anyway
            # so a misconfiguration can't reach file:/ or another scheme.
            if not self.sentinel_api.startswith(("http://", "https://")):
                raise ValueError(f"Refusing to report to non-http(s) URL: {self.sentinel_api!r}")
            data = json.dumps(payload).encode()
            headers = {"Content-Type": "application/json"}
            token = self.token_provider() if self.token_provider is not None else self.auth_token
            if token:
                headers["Authorization"] = f"Bearer {token}"
            req = urllib.request.Request(
                f"{self.sentinel_api.rstrip('/')}/ingest",
                data=data,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2) as r:  # nosec B310 — scheme validated above
                return json.loads(r.read().decode())
        except Exception as exc:  # noqa: BLE001 — fail-open: a Sentinel outage must never block the agent
            self.delivery_failures += 1
            logger.warning(
                "sentinel telemetry delivery failed: endpoint=%s error=%s",
                self.sentinel_api,
                type(exc).__name__,
            )
            return {}

    def report_tool_call(self, *, host: str, tool_name: str, args: str | dict) -> dict:
        """Report an MCP/function tool invocation as a TOOL_CALL event."""
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:  # json.JSONDecodeError
                args = {"raw": args}
        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": args},
            }
        )
        return self.report(host=host, method="POST", path="/mcp/tools/call", request_body=body)

    def report_tool_request(self, *, host: str, tool_name: str, args: str | dict) -> dict:
        """Report a model-proposed tool request; this does not assert execution."""
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:  # json.JSONDecodeError
                args = {"raw": args}
        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "tools/requested",
                "params": {"name": tool_name, "arguments": args},
            }
        )
        return self.report(
            host=host, method="POST", path="/model/tool-requested", request_body=body
        )
