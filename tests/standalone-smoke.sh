#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
TEMP_DIR="$(mktemp -d)"
PROJECT_NAME="windesapi-standalone-$PPID"

cleanup() {
  docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" down --volumes --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT INT TERM

python3 "$ROOT/tests/extract_compose.py" "$ROOT/docs/STUDENTOPDRACHT.md" "$TEMP_DIR/compose.yaml"

export LAB_WORKSPACE="$TEMP_DIR/workspace"
export API_IMAGE="${API_IMAGE:-windesapi-api-lab:dev}"
export CLIENT_IMAGE="${CLIENT_IMAGE:-windesapi-api-client:dev}"
export LAB_PORT="${LAB_PORT:-18080}"

mkdir -p "$TEMP_DIR/workspace"
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" config --quiet
if [ "${SKIP_PULL:-0}" != "1" ]; then
  docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" --profile tools pull
fi
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" run --rm --user 0:0 api lab-reset
test -f "$TEMP_DIR/workspace/app/main.py"
test -f "$TEMP_DIR/workspace/client.py"
test -f "$TEMP_DIR/workspace/rapportage.md"
test -s "$TEMP_DIR/workspace/.api-key"

docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" up -d --wait --wait-timeout 90 api
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" exec -T api lab-status
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" run --rm client \
  python -c 'import os, requests; r=requests.get(os.environ["API_BASE_URL"]+"/api/v1/projects?limit=2", timeout=5); r.raise_for_status(); assert len(r.json()["items"]) == 2; print("clientrequest: OK")'

cp "$ROOT/solution/hardened-settings.json" "$TEMP_DIR/workspace/lab-settings.json"
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" restart api
sleep 2
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" exec -T api lab-status
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" run --rm client \
  python -c 'import os, requests; h={"X-API-Key":os.environ["API_KEY"]}; r=requests.get(os.environ["API_BASE_URL"]+"/api/v1/projects/1", headers=h, timeout=5); r.raise_for_status(); assert r.json()["id"] == 1; print("geharde clientrequest: OK")'
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" exec -T api lab-check
docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" exec -T api lab-log

docker compose --project-name "$PROJECT_NAME" --project-directory "$TEMP_DIR" down --volumes --remove-orphans
test -z "$(docker ps -aq --filter "label=com.docker.compose.project=$PROJECT_NAME")"
test -z "$(docker network ls -q --filter "label=com.docker.compose.project=$PROJECT_NAME")"
