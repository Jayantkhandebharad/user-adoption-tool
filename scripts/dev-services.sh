#!/usr/bin/env bash
# Start, stop or inspect the local development emulators (infra/docker/compose.dev.yaml).
# Usage: scripts/dev-services.sh up|down|reset|ps|logs [service]
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
compose=(docker compose -f "$root/infra/docker/compose.dev.yaml")

case "${1:-}" in
  up)    "${compose[@]}" up -d --wait ;;
  down)  "${compose[@]}" down ;;
  reset) "${compose[@]}" down --volumes ;;  # also deletes the local database
  ps)    "${compose[@]}" ps ;;
  logs)  shift; "${compose[@]}" logs -f "$@" ;;
  *)     echo "usage: $0 up|down|reset|ps|logs [service]" >&2; exit 2 ;;
esac
