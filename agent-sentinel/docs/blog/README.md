# Agent Sentinel — a 10-part series

**Positioning:** Agent Sentinel is an explainable runtime observability and
policy-detection layer for AI agents. It detects, explains, stores, and
exports evidence-rich findings into SOC platforms such as Microsoft Sentinel
and Splunk.

**Current product line:** Detect. Explain. Export.
**Roadmap:** Enforce, through a separately reviewed pre-action gateway. The
current engine produces post-observation findings; it does not block or
quarantine actions.

## Parts released so far

Every part has a plain-English LinkedIn post and a technical write-up (with a
plain-English summary up top) for architects and engineers. The
[traceability matrix](TRACEABILITY.md) ties each claim to its implementation,
its regression test, and its current-versus-roadmap boundary. New parts are
added here as they are released.

| # | Part | LinkedIn post | Technical write-up | Main code | Regression test |
|---|---|---|---|---|---|
| 1 | Why AI Agents Need a Flight Recorder | [post](linkedin/01-why-agents-need-a-flight-recorder.md) | [read](technical-details/01-why-agents-need-a-flight-recorder.md) | `pipeline.py`, `detection/engine.py` | [`test_pipeline.py`](../../app/tests/test_pipeline.py) |

Every link in this folder is relative, so the article, the code, and the tests
always resolve on the same repository version. Run `python scripts/check_links.py`
to verify every relative link and heading anchor.

## Single source of truth

This folder is the only place the series is written, and it lives in the same
repository as the website. [anandnarayanan.net](https://anandnarayanan.net/)
is built from it: each site post is the plain-English part of
`technical-details/NN-*.md` (everything above "Design and implementation")
and its image. `scripts/sync-series.mjs` at the repository root does this at
build time and takes each post's date from `scripts/release-dates.json`.
Edit here, never in the generated site files.
