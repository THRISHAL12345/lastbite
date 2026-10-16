#!/usr/bin/env bash
set -euo pipefail
# Use the API endpoint that is routed by Ingress; fail visibly on HTTP errors.
URL="${URL:-http://relaydesk.local/api/tickets?limit=20}"
REQUESTS="${REQUESTS:-500}"
CONCURRENCY="${CONCURRENCY:-10}"
export URL
seq "$REQUESTS" | xargs -P "$CONCURRENCY" -I '{}' sh -c 'curl --fail --silent --show-error --max-time 10 "$URL" >/dev/null'
echo "Completed $REQUESTS successful requests. Inspect HPA and Grafana; this does not guarantee CPU scaling."
