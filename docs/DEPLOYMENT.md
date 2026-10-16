# Deployment runbook

Run commands from the RelayDesk repository root unless a working directory is shown. These are deployment instructions, not a record of a completed AWS deployment. Use a dedicated demonstration cluster. Choose either direct Helm ownership or Argo CD ownership for the application.

## 1. Build and publish

Push this project as its own GitHub repository. Wait for the `test` and `images` jobs to pass. Set the GHCR packages public for a non-sensitive classroom demo, or create a registry pull secret and set `imagePullSecrets: [{name: ghcr}]` in your environment values. Only promote the SHA of a successful run with both published images:

```bash
python3 scripts/promote.py YOUR_OWNER FULL_40_CHARACTER_COMMIT_SHA
```

Replace the repo URL in `gitops/application.yaml`. Replace the ingress hostname in `values-prod.yaml` with `relaydesk.local` for the local port-forward demo, or a domain you control for a separately secured public deployment. Commit these changes and the generated release values.

## 2. Provision EKS

Requirements: AWS CLI and configured AWS credentials, Terraform >=1.7, kubectl, Helm. Verify your AWS account and role before making changes.

```bash
aws sts get-caller-identity
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit admin_cidrs to your real public IP /32. Do not leave the example address.
terraform -chdir=terraform init
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
terraform -chdir=terraform plan -out=deployment.tfplan
terraform -chdir=terraform apply deployment.tfplan
aws eks update-kubeconfig --region ap-south-1 --name relaydesk-eks
kubectl get nodes
kubectl apply -f k8s/storageclass.yaml
```

Commit the generated `.terraform.lock.hcl` to pin provider selections. Keep state, plan files, credentials and tfvars out of Git. For team use, configure an encrypted S3 state backend with locking and least-privilege access before the first apply. EKS, nodes, NAT, disks and logs incur charges. The admin CIDR can be updated when your public IP changes.

## 3. Bootstrap namespace and database credentials

```bash
kubectl apply -f k8s/namespace.yaml
# Generate a password without storing it in a shell history argument.
DB_PASSWORD="$(openssl rand -hex 24)"
printf '%s' "$DB_PASSWORD" | kubectl create secret generic relaydesk-db \
  -n relaydesk --from-file=password=/dev/stdin
unset DB_PASSWORD
```

Keep a secure copy if needed for recovery. Do not change the Kubernetes secret independently of an initialized database: PostgreSQL initialization variables do not rotate an existing database role password.

The namespace enforces Kubernetes restricted Pod Security. The chart uses explicit users, dropped capabilities, disabled privilege escalation and RuntimeDefault seccomp. Application pods do not mount service account tokens.

## 4. Install ingress, metrics and monitoring prerequisites

The example uses a private Traefik ClusterIP service and port-forwarding, so no cloud load balancer is required. A public service needs a supported AWS load balancer controller, DNS, TLS and application authentication configured separately.

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install traefik traefik/traefik --version 41.7.1 \
  -n ingress-system --create-namespace -f k8s/traefik-values.yaml --wait
helm upgrade --install metrics-server metrics-server/metrics-server \
  -n kube-system --wait
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml \
  --wait --timeout 15m
kubectl apply -f monitoring/dashboard-configmap.yaml
kubectl apply -f monitoring/alerts.yaml
```

For repeatable platform installations, select and record compatible versions of the metrics, monitoring and Argo CD charts before evaluation. These platform charts are installed separately from the app chart. The `monitoring` release name matches the ServiceMonitor and PrometheusRule labels. Default app values keep CRDs and HPA optional so a bare-cluster Helm render is valid.

## 5A. Direct Helm demonstration

```bash
helm upgrade --install relaydesk ./helm/relaydesk -n relaydesk \
  -f helm/relaydesk/values-prod.yaml -f helm/relaydesk/values-release.yaml \
  --wait --wait-for-jobs --timeout 10m
kubectl get pods,svc,ingress,hpa -n relaydesk
helm list -n relaydesk
```

The migration Job is named from the image reference. Use unique SHA tags for every release. Never reuse a tag for different migration content. Helm leaves completed jobs as release resources; later upgrades remove the old job when its name changes. Avoid concurrent Helm upgrades of the same release.

## 5B. Argo CD GitOps demonstration

For the required GitOps walkthrough, bootstrap Argo CD and let it own the app from the start:

```bash
helm upgrade --install argocd argo/argo-cd -n argocd --create-namespace --wait --timeout 10m
kubectl apply -f gitops/application.yaml
kubectl get application relaydesk -n argocd
kubectl port-forward -n argocd svc/argocd-server 8443:443
```

Open https://localhost:8443. Retrieve the initial admin password locally using the Argo CD documentation, sign in, and rotate it. Do not include credentials in the recording. Configure Git credentials in Argo CD if the repository is private.

Argo CD uses Helm as a renderer; an Argo-managed app **does not appear as an installed Helm release in `helm list`**. Show its Helm source configuration and Application resource. If the evaluator requires both forms of evidence, demonstrate direct Helm separately, uninstall its workloads while retaining the PVC, then start Argo CD ownership. Do not run both controllers against the same application at once.

Argo CD applies PostgreSQL at sync wave -2, a Sync migration hook at -1, then the application. The hook is deleted after success and reruns safely on sync. No application schema is created automatically during API startup.

## 6. Reach the application and inspect metrics

For the private ingress demo, set `ingress.host: relaydesk.local` in the environment values and add `127.0.0.1 relaydesk.local` to your local hosts file. In separate terminals:

```bash
kubectl port-forward -n ingress-system svc/traefik 3000:80
kubectl port-forward -n relaydesk svc/relaydesk-backend 8000:8000
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
```

Open http://relaydesk.local:3000 (through Ingress), http://localhost:8000/docs, http://localhost:9090/targets and http://localhost:3001. Alternatively test ingress without changing hosts:

```bash
curl --fail -H 'Host: relaydesk.local' http://127.0.0.1:3000/api/tickets
curl --fail http://localhost:8000/metrics
python3 scripts/seed.py
URL=http://relaydesk.local:3000/api/tickets REQUESTS=1000 bash scripts/load-test.sh
kubectl top pods -n relaydesk
kubectl get hpa -n relaydesk -w
```

Find Grafana's generated admin password in the `monitoring-grafana` secret. Open **RelayDesk · Service health**, select the Prometheus data source, generate traffic and allow two or more scrapes. If panels are empty, check the namespace and ServiceMonitor labels, the Prometheus Targets page, and the selected time window. Requests to `/health`, `/ready` and `/metrics` are excluded from application traffic measurements.

## 7. Rollback and recovery

For Argo CD, revert the promotion commit and push so Git remains authoritative. Use backward-compatible migrations; reverting an image does not undo a database schema change. For direct Helm only, inspect `helm history relaydesk -n relaydesk` and use `helm rollback relaydesk REVISION -n relaydesk --wait`. Capture the migration Job's logs before retrying failures. If the DB PVC is pending, inspect the EBS CSI pods, IAM role, gp3 StorageClass and available zones.

## 8. Cleanup after evaluation

First capture any required evidence and back up data you need. Stop Argo CD reconciliation, remove workload ownership, and delete the optional failure labs. For Argo, this Application has no resources finalizer, so deleting it stops reconciliation without deleting resources; remove its workloads explicitly:

```bash
kubectl delete application relaydesk -n argocd --ignore-not-found
kubectl delete -n relaydesk deployment,service,statefulset,job,ingress,hpa --all
# If you used direct Helm instead:
# helm uninstall relaydesk -n relaydesk
kubectl get pvc -n relaydesk
kubectl get pv
```

The StatefulSet PVC and gp3 EBS volume retain data. After you explicitly decide to discard the demo database, delete its PVC, identify the retained PV's `spec.csi.volumeHandle`, remove the PV, and delete that exact detached EBS volume in AWS. Verify account, region and volume ID before deletion. Never issue a bulk volume deletion.

Uninstall `traefik`, `monitoring`, and `argocd` with their namespaces if installed solely for this demo; verify there are no cloud load balancers or retained disks. Then:

```bash
terraform -chdir=terraform plan -destroy
terraform -chdir=terraform destroy
```

Capture the completion output and check AWS for leftover disks, load balancers and logs. Store any evidence without secrets.
