"""Alerter/SIEM export: "not installed" is not a delivery failure.

A build can leave out the alerting and SIEM packages (the public copy did
until Part 4 of the series). A missing package must log once at INFO and leave
the failure counters alone; a package that is present but fails (including an
import error inside it) must still log a warning and count as a failure.
"""

from __future__ import annotations

import logging
import sys
import types
from pathlib import Path

import pytest
from sentinel import pipeline
from sentinel.collector.parsers import parse_flow
from sentinel.detection.engine import Engine
from sentinel.detection.policy import PolicySet

POLICY = Path(__file__).resolve().parents[2] / "policies" / "example.yaml"


@pytest.fixture
def finding():
    engine = Engine(PolicySet.from_yaml(POLICY))
    event = parse_flow(
        agent_id="recon-bot",
        session_id="s",
        host="attacker-exfil.example",
        method="POST",
        path="/c",
        request_body="x",
    )
    return engine.evaluate(event)[0]


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    monkeypatch.setattr(pipeline, "_export_failures", {"alerter": 0, "siem": 0})
    monkeypatch.setattr(pipeline, "_export_not_installed", set(), raising=False)
    for name in (
        "sentinel.alerting",
        "sentinel.alerting.webhook",
        "sentinel.siem",
        "sentinel.siem.log_analytics",
    ):
        monkeypatch.delitem(sys.modules, name, raising=False)


def _install(monkeypatch, package: str, module: str, **attrs) -> None:
    pkg = types.ModuleType(package)
    pkg.__path__ = []  # mark as a package
    mod = types.ModuleType(f"{package}.{module}")
    for k, v in attrs.items():
        setattr(mod, k, v)
    monkeypatch.setitem(sys.modules, package, pkg)
    monkeypatch.setitem(sys.modules, f"{package}.{module}", mod)


def test_missing_packages_are_not_failures_and_log_once(finding, monkeypatch, caplog):
    # None in sys.modules makes the import fail as if the package weren't there,
    # whether or not this checkout includes it.
    monkeypatch.setitem(sys.modules, "sentinel.alerting", None)
    monkeypatch.setitem(sys.modules, "sentinel.siem", None)
    with caplog.at_level(logging.INFO, logger="sentinel.pipeline"):
        for _ in range(3):
            pipeline._fire_alerter(finding)
            pipeline._push_siem(finding)

    assert pipeline.export_failures() == {"alerter": 0, "siem": 0}
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
    infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert len(infos) == 2  # once per export kind, not once per finding
    assert any("sentinel.alerting" in m for m in infos)
    assert any("sentinel.siem" in m for m in infos)


def test_installed_module_that_raises_is_a_failure(finding, monkeypatch, caplog):
    def boom(_finding):
        raise RuntimeError("webhook down")

    _install(monkeypatch, "sentinel.alerting", "webhook", fire=boom)
    _install(monkeypatch, "sentinel.siem", "log_analytics", push=boom)

    with caplog.at_level(logging.WARNING, logger="sentinel.pipeline"):
        pipeline._fire_alerter(finding)
        pipeline._push_siem(finding)

    assert pipeline.export_failures() == {"alerter": 1, "siem": 1}
    messages = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert any("alert delivery failed" in m and "webhook down" in m for m in messages)
    assert any("SIEM export failed" in m for m in messages)


def test_installed_module_missing_its_own_dependency_is_a_failure(finding, monkeypatch):
    def needs_requests(_finding):
        raise ModuleNotFoundError("No module named 'requests'", name="requests")

    _install(monkeypatch, "sentinel.alerting", "webhook", fire=needs_requests)
    pipeline._fire_alerter(finding)
    assert pipeline.export_failures()["alerter"] == 1


def test_successful_export_counts_nothing(finding, monkeypatch, caplog):
    delivered = []
    _install(monkeypatch, "sentinel.alerting", "webhook", fire=delivered.append)
    _install(monkeypatch, "sentinel.siem", "log_analytics", push=delivered.append)
    with caplog.at_level(logging.INFO, logger="sentinel.pipeline"):
        pipeline._fire_alerter(finding)
        pipeline._push_siem(finding)
    assert delivered == [finding, finding]
    assert pipeline.export_failures() == {"alerter": 0, "siem": 0}
    assert not caplog.records


def test_a_real_webhook_outage_is_counted(finding, monkeypatch):
    """The real alerter, not a stand-in: a target that is down must reach the counter."""
    from sentinel.alerting import webhook

    monkeypatch.setattr(webhook, "_THRESHOLD", "high")
    monkeypatch.setattr(webhook, "_TEAMS_WEBHOOK", "https://example.test/teams")
    monkeypatch.setattr(webhook, "_PAGERDUTY_KEY", "")
    monkeypatch.setattr(webhook, "_SLACK_WEBHOOK", "")

    def down(url, payload, headers=None):
        raise OSError("connection refused")

    monkeypatch.setattr(webhook, "_post", down)

    pipeline._fire_alerter(finding)  # must not raise

    assert pipeline.export_failures()["alerter"] == 1


def test_a_real_log_analytics_outage_is_counted(finding, monkeypatch):
    """The real SIEM connector, not a stand-in: a failed upload must reach the counter."""
    from sentinel.siem import log_analytics

    class Down:
        def upload(self, **_kwargs):
            raise OSError("ingestion endpoint unreachable")

    monkeypatch.setattr(log_analytics, "_ACTIVE", True)
    monkeypatch.setattr(log_analytics, "_client", None)
    monkeypatch.setattr(log_analytics, "_get_client", Down)

    pipeline._push_siem(finding)  # must not raise

    assert pipeline.export_failures()["siem"] == 1
