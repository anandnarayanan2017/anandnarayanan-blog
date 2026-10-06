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
| `Dockerfile`, `docker-compose.yml` | Container image and the local stack (Sentinel + PostgreSQL + optional simulator) |

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

## Run it with Docker

Needs only Docker (with the compose plugin): no Python setup, no cloud account.

```bash
cd agent-sentinel
docker compose up --build -d            # Agent Sentinel on PostgreSQL; dashboard at http://localhost:8000
docker compose --profile demo up -d     # ...plus the fintech simulator, so the dashboard fills with live findings
docker compose down -v                  # stop and delete the database
scripts/docker_e2e.sh                   # build, start, run every end-to-end check, tear down;
                                        # results in e2e-docker-report.json
```

Authentication is off in this stack (`SENTINEL_DEV_MODE=1`) and the port is
published on 127.0.0.1 only; never expose it as is. CI runs
`scripts/docker_e2e.sh` on every pull request that touches this folder.

## Follow along part by part

Each part is tagged when it is published: `agent-sentinel-part-1`,
`agent-sentinel-part-2`, and so on ([tags](https://github.com/anandnarayanan2017/anandnarayanan-blog/tags)).
Check out a tag to see the code exactly as that part describes it:

```bash
git clone https://github.com/anandnarayanan2017/anandnarayanan-blog
cd anandnarayanan-blog && git checkout agent-sentinel-part-1
cd agent-sentinel && docker compose up --build -d
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

