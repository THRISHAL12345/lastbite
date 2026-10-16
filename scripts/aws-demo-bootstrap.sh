#!/usr/bin/env bash
# Install the classroom stack after Terraform apply. Does not provision AWS.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/platform-versions.sh
: "${AWS_PROFILE:?Set your configured AWS profile}"
: "${KUBECONFIG:?Use a dedicated kubeconfig for this AWS demo}"
export AWS_REGION="${AWS_REGION:-ap-south-1}"
cluster="$(terraform -chdir=terraform output -raw cluster_name)"
endpoint="$(terraform -chdir=terraform output -raw cluster_endpoint)"
test "$cluster" = lastbite-eks || { echo 'Expected the dedicated lastbite-eks demo.' >&2; exit 1; }
aws eks update-kubeconfig --region "$AWS_REGION" --name "$cluster" --kubeconfig "$KUBECONFIG"
test "$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')" = "$endpoint"
kubectl wait nodes --all --for=condition=Ready --timeout=5m
kubectl apply -f k8s/namespace.yaml -f k8s/storageclass.yaml
if ! kubectl get secret lastbite-db -n lastbite >/dev/null 2>&1; then
  openssl rand -hex 24 | tr -d '\n' | kubectl create secret generic lastbite-db \
    -n lastbite --from-file=password=/dev/stdin
fi
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update traefik metrics-server prometheus-community
helm upgrade --install traefik traefik/traefik --version "$TRAEFIK_CHART_VERSION" \
  -n ingress-system --create-namespace -f k8s/traefik-values.yaml --wait --timeout 5m
helm upgrade --install metrics-server metrics-server/metrics-server --version "$METRICS_SERVER_CHART_VERSION" \
  -n kube-system --wait --timeout 5m
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version "$MONITORING_CHART_VERSION" \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml -f monitoring/values-demo.yaml \
  --wait --timeout 10m
kubectl apply -f monitoring/dashboard-configmap.yaml -f monitoring/alerts.yaml
helm upgrade --install lastbite helm/lastbite -n lastbite \
  -f helm/lastbite/values-prod.yaml -f helm/lastbite/values-release.yaml \
  --set ingress.host=localhost \
  --wait --wait-for-jobs --timeout 10m
kubectl rollout status deployment/lastbite-backend -n lastbite --timeout=3m
kubectl rollout status deployment/lastbite-frontend -n lastbite --timeout=3m
mkdir -p artifacts/lastbite/aws
kubectl get nodes -o wide > artifacts/lastbite/aws/nodes.txt
kubectl get pods,svc,ingress,hpa -n lastbite -o wide > artifacts/lastbite/aws/resources.txt
kubectl get deployment -n lastbite -o json > artifacts/lastbite/aws/deployments.json
helm list -A > artifacts/lastbite/aws/helm-list.txt
echo 'AWS Helm demo is ready. Use the dedicated KUBECONFIG for access and cleanup.'
