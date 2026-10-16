#!/usr/bin/env bash
# Keep this process running while using the browser. Ctrl-C stops only its forwards.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p artifacts/access
pids=()
cleanup() { for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT
forward() {
  kubectl port-forward -n "$1" "svc/$2" "$3" > "artifacts/access/$2.log" 2>&1 &
  pids+=("$!")
}
forward ingress-system traefik 3000:80
forward relaydesk relaydesk-backend 8000:8000
forward monitoring monitoring-kube-prometheus-prometheus 9090:9090
forward monitoring monitoring-grafana 3001:80
forward argocd argocd-server 8443:443
echo 'App: http://relaydesk.local:3000 (hosts entry 127.0.0.1 relaydesk.local required)'
echo 'API: http://localhost:8000/docs | Prometheus: http://localhost:9090/targets'
echo 'Grafana: http://localhost:3001 | Argo CD: https://localhost:8443'
echo 'Credential retrieval commands are in docs/YOUR-NEXT-STEPS.md. Do not record credentials.'
wait
