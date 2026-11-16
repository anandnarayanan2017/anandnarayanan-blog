"""An agent with no policy entry is itself a finding (`identity.unregistered_agent`).

Under `policies/example.yaml` there is no `default_policy`, so the finding is
all an unknown agent gets. Under `policies/fintech.yaml` the `default_policy`
is also applied to it.
"""

from pathlib import Path

import pytest
from sentinel.collector.parsers import parse_flow
from sentinel.detection.engine import IDENTITY_CONTROL_REFS, Engine
from sentinel.detection.policy import PolicySet
from sentinel.schema.events import Severity

POLICIES = Path(__file__).resolve().parents[1].parent / "policies"


@pytest.fixture
def engine():
    return Engine(PolicySet.from_yaml(POLICIES / "example.yaml"))


@pytest.fixture
def fintech_engine():
    return Engine(PolicySet.from_yaml(POLICIES / "fintech.yaml"))


def _event(agent_id, session_id="s1", host="ledger.internal"):
    return parse_flow(agent_id=agent_id, session_id=session_id, host=host, method="GET", path="/t")


def _identity_findings(findings):
    return [f for f in findings if f.rule_id == "identity.unregistered_agent"]


def test_unknown_agent_is_flagged_before_it_breaks_any_rule(engine):
    """The host is one a known agent may use; the identity alone is the finding."""
    findings = engine.evaluate(_event("shadow-bot"))

    assert [f.rule_id for f in findings] == ["identity.unregistered_agent"]
    finding = findings[0]
    assert finding.severity == Severity.MEDIUM
    assert finding.agent_id == "shadow-bot"
    assert "shadow-bot" in finding.explanation
    assert finding.policy_clause == "no policy entry and no default_policy configured"


def test_registered_agent_is_not_flagged(engine):
    assert engine.evaluate(_event("recon-bot")) == []


def test_finding_is_raised_once_per_session_not_once_per_event(engine):
    counts = [len(_identity_findings(engine.evaluate(_event("shadow-bot")))) for _ in range(5)]

    assert counts == [1, 0, 0, 0, 0]


def test_a_new_session_of_the_same_unknown_agent_is_flagged_again(engine):
    engine.evaluate(_event("shadow-bot", session_id="s1"))

    assert len(_identity_findings(engine.evaluate(_event("shadow-bot", session_id="s2")))) == 1


def test_without_a_default_policy_the_engine_supplies_the_control_references(engine):
    finding = engine.evaluate(_event("shadow-bot"))[0]

    assert finding.control_refs == IDENTITY_CONTROL_REFS


def test_with_a_default_policy_its_clauses_are_applied_to_the_unknown_agent(fintech_engine):
    """`fintech.yaml` has a default policy, so an unlisted host is flagged too."""
    default = fintech_engine.policies.default_policy
    findings = fintech_engine.evaluate(_event("shadow-bot", host="attacker-exfil.example"))

    assert {f.rule_id for f in findings} == {"identity.unregistered_agent", "net.host_not_allowed"}
    identity = _identity_findings(findings)[0]
    assert identity.policy_clause.startswith("default_policy")
    assert identity.control_refs == default.control_refs
