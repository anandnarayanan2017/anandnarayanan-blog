# Agent Sentinel (blog companion)

Code, tests, and write-ups for the **Agent Sentinel** series on
[anandnarayanan.net](https://anandnarayanan.net/): an explainable runtime
observability and policy-detection layer for AI agents in regulated
environments.

```text
Detect. Explain. Export.   (Enforce is roadmap)
```

Start at [`docs/blog/README.md`](docs/blog/README.md). Each released part has a
plain-English LinkedIn post, a technical write-up, the code it cites, and its
tests. Parts are released weekly; this folder grows with them.

## Layout

| Path | What it holds |
|---|---|
| `docs/blog/` | LinkedIn posts, technical write-ups, images, traceability matrix |
| `app/sentinel/` | Event schema, flow parser, detection engine, explainer, storage, API |
| `app/tests/` | Regression tests the traceability matrix points at |
| `policies/` | Example policy files |
| `examples/phase1/`, `dashboard/` | The demo agent, the fintech traffic simulator and the CISO dashboard |

## Run the tests

```bash
cd agent-sentinel
python -m venv .venv && . .venv/bin/activate
pip install -e ".[auth,postgres]" pytest httpx
python -m pytest -q -m "not integration"
```

## Run it end to end

```bash
python scripts/e2e.py               # starts the server, sends good and bad agent traffic,
                                    # checks the findings, the APIs and the dashboard HTML
python scripts/e2e.py --shots out   # also opens the dashboard in headless Chromium
                                    # (needs `pip install playwright`) and saves screenshots
python scripts/check_links.py       # every relative link and anchor in the write-ups
```

To explore by hand: `SENTINEL_DEV_MODE=1 SENTINEL_POLICY=policies/fintech.yaml sentinel serve`,
open <http://localhost:8000>, and in a second terminal run
`python examples/phase1/fintech_sim/sim.py` (or `sentinel demo` for the scripted attack).
Dev mode turns authentication off; never use it on a reachable host.

## References you can't follow from here

This is a trimmed copy of the private Agent Sentinel product repository. Code
comments cite documents that stay there: `design/DESIGN.md`, `spec/*.md`,
review IDs such as `CR-16`, and ADRs other than
[ADR-0001](docs/adr/0001-rules-first-detection.md). They explain why the code
is the way it is; nothing here needs them to build, run or test.

