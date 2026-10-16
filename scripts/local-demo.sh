#!/usr/bin/env bash
# Build an isolated, persistent local demo for rehearsal without AWS.
set -euo pipefail
cd "$(dirname "$0")/.."
for tool in kind docker kubectl helm node python3 git; do
  command -v "$tool" >/dev/null || { echo "Install $tool before continuing." >&2; exit 1; }
done
if kind get clusters | grep -qx relaydesk-demo; then
  echo 'relaydesk-demo already exists. Use scripts/demo-access.sh to reopen it.' >&2
  echo 'To intentionally discard that demo first: kind delete cluster --name relaydesk-demo' >&2
  exit 1
fi
git diff --quiet -- backend frontend helm || { echo 'Commit application changes before building evidence.' >&2; exit 1; }
export REPO_REVISION="$(git rev-parse HEAD)"
export IMAGE_TAG="$REPO_REVISION"
export IMAGE_PREFIX=relaydesk-demo
export KIND_CLUSTER_NAME=relaydesk-demo
docker info >/dev/null
npm --prefix frontend ci
node frontend/node_modules/playwright/cli.js install chromium
docker build -t "$IMAGE_PREFIX-backend:$IMAGE_TAG" backend
docker build -t "$IMAGE_PREFIX-frontend:$IMAGE_TAG" frontend
kind create cluster --name relaydesk-demo --wait 180s
bash scripts/check-kubernetes.sh
bash scripts/check-monitoring.sh
bash scripts/check-gitops.sh
echo 'Local demo is ready. Keep Docker running; open UIs with bash scripts/demo-access.sh.'
