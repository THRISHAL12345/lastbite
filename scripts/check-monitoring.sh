#!/usr/bin/env bash
set -euo pipefail
source scripts/platform-versions.sh
mkdir -p artifacts/monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update prometheus-community
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --version "$MONITORING_CHART_VERSION" -n monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml -f monitoring/values-demo.yaml \
  --wait --timeout 10m
kubectl apply -f monitoring/dashboard-configmap.yaml -f monitoring/alerts.yaml
# Enable monitoring for the already installed application without changing its images.
helm upgrade lastbite helm/lastbite -n lastbite --reuse-values \
  --set monitoring.enabled=true --wait --wait-for-jobs --timeout 5m
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090 > artifacts/monitoring/prometheus-forward.log 2>&1 &
PROM_PID=$!
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80 > artifacts/monitoring/grafana-forward.log 2>&1 &
GRAFANA_PID=$!
kubectl port-forward -n lastbite svc/lastbite-backend 8100:8000 > artifacts/monitoring/backend-forward.log 2>&1 &
BACKEND_PID=$!
trap 'kill "$PROM_PID" "$GRAFANA_PID" "$BACKEND_PID" 2>/dev/null || true' EXIT
python3 scripts/check-monitoring.py
node scripts/capture-monitoring.mjs
kubectl get pods,svc -n monitoring -o wide > artifacts/monitoring/resources.txt
kubectl get servicemonitor -n lastbite -o yaml > artifacts/monitoring/servicemonitor.yaml
helm list -n monitoring > artifacts/monitoring/helm-list.txt
