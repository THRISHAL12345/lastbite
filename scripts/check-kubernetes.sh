#!/usr/bin/env bash
# CI-only integration check in a named disposable Kind cluster.
set -euo pipefail
: "${IMAGE_PREFIX:?Set IMAGE_PREFIX to the built image repository prefix}"
: "${IMAGE_TAG:?Set IMAGE_TAG to the built commit SHA}"
CLUSTER_NAME="${KIND_CLUSTER_NAME:-relaydesk-ci}"
if [[ "$(kubectl config current-context)" != "kind-$CLUSTER_NAME" ]]; then
  echo "Refusing to run outside the disposable kind-$CLUSTER_NAME context." >&2
  exit 1
fi
mkdir -p artifacts/kubernetes
kind load docker-image "$IMAGE_PREFIX-backend:$IMAGE_TAG" "$IMAGE_PREFIX-frontend:$IMAGE_TAG" --name "$CLUSTER_NAME"
kubectl apply -f k8s/namespace.yaml
# This password belongs only to the disposable CI cluster.
printf '%s' 'ci-only-disposable-password' | kubectl create secret generic relaydesk-db \
  -n relaydesk --from-file=password=/dev/stdin
helm repo add traefik https://traefik.github.io/charts
helm repo update traefik
helm upgrade --install traefik traefik/traefik --version 41.7.1 \
  -n ingress-system --create-namespace -f k8s/traefik-values.yaml --wait --timeout 5m
helm upgrade --install relaydesk helm/relaydesk -n relaydesk \
  --set-string backend.repository="$IMAGE_PREFIX-backend" \
  --set-string backend.tag="$IMAGE_TAG" \
  --set-string frontend.repository="$IMAGE_PREFIX-frontend" \
  --set-string frontend.tag="$IMAGE_TAG" \
  --set ingress.enabled=true --set ingress.host=relaydesk.local \
  --wait --wait-for-jobs --timeout 10m
kubectl rollout status deployment/relaydesk-backend -n relaydesk --timeout=120s
kubectl rollout status deployment/relaydesk-frontend -n relaydesk --timeout=120s
for component in backend frontend; do
  test "$(kubectl get deployment "relaydesk-$component" -n relaydesk -o jsonpath='{.status.availableReplicas}')" = 2
done
kubectl get pods,svc,ingress -n relaydesk -o wide > artifacts/kubernetes/resources.txt
helm list -n relaydesk > artifacts/kubernetes/helm-list.txt
kubectl get deployment -n relaydesk -o json > artifacts/kubernetes/deployments.json
kubectl get jobs -n relaydesk -o json > artifacts/kubernetes/migrations.json
kubectl port-forward -n ingress-system svc/traefik 3100:80 > artifacts/kubernetes/ingress-port-forward.log 2>&1 &
INGRESS_PID=$!
kubectl port-forward -n relaydesk svc/relaydesk-backend 8100:8000 > artifacts/kubernetes/backend-port-forward.log 2>&1 &
BACKEND_PID=$!
trap 'kill "$INGRESS_PID" "$BACKEND_PID" 2>/dev/null || true' EXIT
for attempt in $(seq 1 30); do
  if curl --fail --silent --max-time 2 http://127.0.0.1:8100/ready >/dev/null \
     && curl --fail --silent --max-time 2 -H 'Host: relaydesk.local' http://127.0.0.1:3100/api/tickets >/dev/null; then
    break
  fi
  sleep 2
done
python3 scripts/smoke.py --frontend-url http://127.0.0.1:3100 \
  --backend-url http://127.0.0.1:8100 --host relaydesk.local \
  --output artifacts/kubernetes/smoke.json
curl --fail --silent --show-error http://127.0.0.1:8100/metrics > artifacts/kubernetes/metrics.txt
