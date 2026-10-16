#!/usr/bin/env bash
# Transfer the disposable demo from Helm CLI ownership to Argo CD, then prove self-heal.
set -euo pipefail
source scripts/platform-versions.sh
: "${IMAGE_PREFIX:?Set the image repository prefix}"
: "${IMAGE_TAG:?Set the already tested image tag}"
: "${REPO_REVISION:?Set a full source commit already pushed to GitHub}"
case "$(kubectl config current-context)" in
  kind-lastbite-ci|kind-lastbite-demo) ;;
  *) echo 'This ownership-transfer check is only for the dedicated Kind demo/CI cluster.' >&2; exit 1;;
esac
mkdir -p artifacts/gitops
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update argo
helm upgrade --install argocd argo/argo-cd --version "$ARGOCD_CHART_VERSION" \
  -n argocd --create-namespace -f gitops/values-demo.yaml --wait --timeout 10m
# StatefulSet PVCs are retained. Never let Helm CLI and Argo manage these workloads together.
helm uninstall lastbite -n lastbite --wait --timeout 5m
python3 scripts/demo-application.py | kubectl apply -f -
kubectl wait -n argocd application/lastbite --for=jsonpath='{.status.sync.status}'=Synced --timeout=600s
kubectl wait -n argocd application/lastbite --for=jsonpath='{.status.health.status}'=Healthy --timeout=300s
kubectl get application lastbite -n argocd -o json > artifacts/gitops/application-before-drift.json
test "$(kubectl get application lastbite -n argocd -o jsonpath='{.status.sync.revision}')" = "$REPO_REVISION"
kubectl scale deployment/lastbite-frontend -n lastbite --replicas=1
kubectl get deployment lastbite-frontend -n lastbite -o json > artifacts/gitops/deployment-drift.json
for attempt in $(seq 1 60); do
  if [[ "$(kubectl get deployment lastbite-frontend -n lastbite -o jsonpath='{.spec.replicas}')" = 2 ]]; then
    break
  fi
  sleep 2
done
test "$(kubectl get deployment lastbite-frontend -n lastbite -o jsonpath='{.spec.replicas}')" = 2
kubectl rollout status deployment/lastbite-frontend -n lastbite --timeout=180s
kubectl wait -n argocd application/lastbite --for=jsonpath='{.status.sync.status}'=Synced --timeout=180s
kubectl wait -n argocd application/lastbite --for=jsonpath='{.status.health.status}'=Healthy --timeout=180s
kubectl get application lastbite -n argocd -o json > artifacts/gitops/application.json
kubectl get deployment lastbite-frontend -n lastbite -o json > artifacts/gitops/deployment-healed.json
kubectl get pods,svc,ingress -n lastbite -o wide > artifacts/gitops/resources.txt
kubectl port-forward -n argocd svc/argocd-server 8443:443 > artifacts/gitops/server-forward.log 2>&1 &
ARGO_PID=$!
kubectl port-forward -n lastbite svc/lastbite-backend 8100:8000 > artifacts/gitops/backend-forward.log 2>&1 &
BACKEND_PID=$!
kubectl port-forward -n ingress-system svc/traefik 3100:80 > artifacts/gitops/ingress-forward.log 2>&1 &
INGRESS_PID=$!
trap 'kill "$ARGO_PID" "$BACKEND_PID" "$INGRESS_PID" 2>/dev/null || true' EXIT
for attempt in $(seq 1 30); do
  if curl --fail --silent --max-time 2 http://127.0.0.1:8100/ready >/dev/null \
     && curl --fail --silent --max-time 2 -H 'Host: lastbite.local' http://127.0.0.1:3100/api/listings >/dev/null; then break; fi
  sleep 2
done
python3 scripts/smoke.py --frontend-url http://127.0.0.1:3100 --backend-url http://127.0.0.1:8100 \
  --host lastbite.local --output artifacts/gitops/smoke.json
node scripts/capture-gitops.mjs
echo 'PASS: pinned Git revision is Synced/Healthy; manual replica drift was repaired automatically.'
