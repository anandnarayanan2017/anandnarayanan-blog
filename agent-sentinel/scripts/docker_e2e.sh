#!/usr/bin/env bash
# End-to-end test of the Docker stack: build the image, start Agent Sentinel on
# PostgreSQL with docker compose, run scripts/e2e.py against it, tear it down.
#
#   scripts/docker_e2e.sh                  # API, traffic, audit chain, approvals
#   scripts/docker_e2e.sh --browser        # ...plus the dashboard in headless Chromium
#   scripts/docker_e2e.sh --shots out      # ...and screenshots into ./out
#
# Writes e2e-docker-report.json (or $E2E_REPORT). Needs Docker with the compose
# plugin and port 8000 free. Uses project name agent-sentinel-e2e so it never
# touches a stack you started yourself.
set -euo pipefail
cd "$(dirname "$0")/.."

export COMPOSE_PROJECT_NAME=agent-sentinel-e2e
REPORT="${E2E_REPORT:-e2e-docker-report.json}"

cleanup() {
  status=$?
  if (( status != 0 )); then
    echo "--- sentinel logs (last 80 lines) ---"
    docker compose logs --no-color --tail 80 sentinel || true
  fi
  docker compose down -v --remove-orphans >/dev/null 2>&1 || true
  exit "$status"
}
trap cleanup EXIT

docker compose up --build --detach --wait --wait-timeout 180
docker compose ps
python3 scripts/e2e.py --url http://localhost:8000 --postgres --report "$REPORT" "$@"
