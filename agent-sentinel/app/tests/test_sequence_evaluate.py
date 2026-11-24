"""evaluate(): the calibrated threshold, per-attack recall, and the Part 3 figures.

A loop variable once shadowed the calibrated threshold, so every per-attack
recall was computed against the highest score in the PR sweep and came out 0.
These tests pin the threshold, the per-attack recall, and the numbers the
Part 3 write-up quotes, so the article and the code cannot drift apart quietly.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from sentinel_sequence.evaluate import evaluate

FOLDER = Path(__file__).resolve().parents[2]


def test_threshold_is_the_normal_percentile_not_a_sweep_value():
    normal = [float(x) for x in range(1, 101)]  # 1..100
    attacks = [("a", 200.0), ("b", 0.5)]
    rep = evaluate(normal, attacks, percentile=99.0)
    assert rep.threshold == pytest.approx(float(np.percentile(normal, 99.0)))
    assert rep.threshold < 200.0


def test_per_attack_recall_uses_the_calibrated_threshold():
    normal = [1.0] * 99 + [2.0]
    attacks = [("loud", 10.0), ("loud", 9.0), ("quiet", 0.5), ("mixed", 10.0), ("mixed", 0.5)]
    rep = evaluate(normal, attacks)
    assert rep.per_attack_recall == {"loud": 1.0, "mixed": 0.5, "quiet": 0.0}
    assert rep.recall == pytest.approx(3 / 5)


def test_pr_curve_still_sweeps_every_candidate():
    normal = [1.0, 2.0, 3.0]
    attacks = [("a", 4.0)]
    rep = evaluate(normal, attacks)
    assert [round(t, 6) for t, _, _ in rep.pr_curve] == [1.0, 2.0, 3.0, 4.0]


def test_payments_demo_reproduces_the_part_3_figures():
    out = subprocess.run(
        [sys.executable, "examples/phase2/sequence_eval_payments_demo.py"],
        cwd=FOLDER,
        capture_output=True,
        text=True,
        timeout=300,
        check=True,
    ).stdout
    scores = re.findall(r"(mean-NLL|top-3 surprise)\s*: P=([\d.]+) R=([\d.]+) F1=([\d.]+)", out)
    assert [s[1:] for s in scores] == [
        ("0.976", "0.830", "0.897"),  # order-1, mean NLL
        ("0.972", "0.700", "0.814"),  # order-1, top-3 surprise
        ("0.974", "0.740", "0.841"),  # order-2, mean NLL
        ("0.987", "0.770", "0.865"),  # order-2, top-3 surprise (the pipeline's choice)
    ]
    recall = dict(re.findall(r"^\s+([a-z_+]+)\s+([\d.]+)$", out, re.MULTILINE))
    assert recall["exfiltration_burst"] == "0.000"
    assert recall["unauthorized_override"] == "0.167"
    assert recall["limit_bypass"] == "0.500"
    assert recall["order_abuse"] == "0.875"
    for single in ("burst_loop", "credential_probe", "silent_cancel_replay"):
        assert recall[single] == "1.000"
    multi = {k: v for k, v in recall.items() if "+" in k}
    assert len(multi) == 17 and set(multi.values()) == {"1.000"}
    assert "surprise 4.95 > threshold 4.37" in out
    assert "observed tool:verify_2fa (p=0.0064)" in out
