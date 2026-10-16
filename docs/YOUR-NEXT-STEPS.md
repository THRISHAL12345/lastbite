# Your remaining steps to finish the capstone

Repository: https://github.com/THRISHAL12345/relaydesk

Run commands from the `relaydesk` directory. The application and its local/CI
demonstrations do not require AWS. The remaining cloud marks require a real AWS
account, and the mandatory presentation requires you to explain and record the project.
Do not send credentials in chat or include them in screenshots or videos.

## 1. Configure your AWS access locally

For a normal AWS Console IAM/federated login, your installed AWS CLI supports a
browser sign-in without creating long-lived access keys:

```bash
aws login --profile relaydesk-console
aws configure set credential_process "aws configure export-credentials --profile relaydesk-console --format process" --profile relaydesk
aws configure set region ap-south-1 --profile relaydesk
```

Select the intended account/role in your browser and use `ap-south-1` when prompted
for the deployment region. The second profile lets the pinned Terraform AWS provider
obtain the temporary credentials through the CLI. Your IAM identity needs
`SignInLocalDevelopmentAccess` as well as the deployment permissions listed below.
See [AWS's console-login and credential-process instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
Renew this session with `aws login --profile relaydesk-console` when it expires.

If your account uses IAM Identity Center (SSO):

```bash
aws configure sso --profile relaydesk
aws sso login --profile relaydesk
```

Enter the SSO start URL and SSO region supplied by your AWS administrator, and choose
the intended account and role. The SSO region may differ from the deployment region.

If you use IAM access keys instead, configure them only in your own terminal:

```bash
aws configure --profile relaydesk
```

Use an IAM identity authorized to manage the demo's VPC, EKS, EC2 node groups,
IAM roles/policies, EBS CSI, KMS and CloudWatch resources. Do not use root access keys.
If your identity lacks permissions, ask your account administrator to grant the
required deployment role; a login alone does not grant infrastructure permissions.

```bash
export AWS_PROFILE=relaydesk
export AWS_REGION=ap-south-1
bash scripts/aws-preflight.sh
```

Check the account number in the output. The helper verifies identity, prepares an
ignored `terraform.tfvars` with your public IPv4 `/32`, initializes Terraform and
validates it. It does **not** provision anything. If an existing tfvars file remains
from an earlier attempt, review it: region, cluster name and administrator IP must
match your intended environment. Refresh SSO with `aws sso login` if it expires.

## 2. Provision AWS and capture the evidence

EKS, EC2 workers, NAT, logs and disks incur charges while running. Use a dedicated
demo account/environment and complete the cleanup section after evaluation.

```bash
mkdir -p artifacts/aws
terraform -chdir=terraform plan -out=deployment.tfplan
terraform -chdir=terraform show -no-color deployment.tfplan > artifacts/aws/plan.txt
```

Review the plan before continuing. Expect the VPC, two public/two private subnets,
NAT, EKS, managed node group and related IAM/security resources. Capture the terminal
plan summary. Stop and resolve permission, quota or unsupported-version errors.

```bash
terraform -chdir=terraform apply deployment.tfplan
aws eks update-kubeconfig --profile relaydesk --region ap-south-1 --name relaydesk-eks
kubectl get nodes -o wide
kubectl apply -f k8s/storageclass.yaml
kubectl apply -f k8s/namespace.yaml
```

Capture the successful apply output, Ready nodes, AWS Console VPC/subnets and EKS
cluster/node group in **ap-south-1**. If you changed the region or cluster name,
change the command accordingly. Keep Terraform state/plan files private and intact
until destruction; never add them to Git.

## 3. Use a published image release and prepare the database

The committed `values-release.yaml` identifies the verified release to deploy;
its source run is linked in [the evidence index](../demo/evidence/README.md).
For a later release, choose a green run and copy its complete source SHA. Both
images must have been published by that run. Public GitHub repositories do not
automatically make GHCR packages public. For this classroom project, open each
package's settings and make the backend and frontend packages public. Open your
GitHub profile → Packages → `relaydesk-backend` / `relaydesk-frontend` → Package
settings → Change visibility → Public. Capture each package page showing its SHA tag.
If your account requires private packages, create a registry pull secret and add
`imagePullSecrets: [{name: ghcr}]` to the environment values before deploying.

Only if promoting a newer release:

```bash
python3 scripts/promote.py THRISHAL12345 FULL_SHA_FROM_SUCCESSFUL_RUN
git diff -- helm/relaydesk/values-release.yaml
```

The production values already use `ingress.host: relaydesk.local` for the private
port-forward demonstration and `database.storageClass: gp3` for EKS. If you promoted
a newer release, commit and push its reviewed values:

```bash
git add helm/relaydesk/values-release.yaml helm/relaydesk/values-prod.yaml
git commit -m "Promote verified RelayDesk images for the EKS demonstration"
git push
```

Create the database secret once in the new namespace (do not rotate it independently
of an initialized PostgreSQL database):

```bash
openssl rand -hex 24 | tr -d '\n' | kubectl create secret generic relaydesk-db \
  -n relaydesk --from-file=password=/dev/stdin
```

## 4. Install the platform and application

```bash
source scripts/platform-versions.sh
helm repo add traefik https://traefik.github.io/charts
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install traefik traefik/traefik --version "$TRAEFIK_CHART_VERSION" \
  -n ingress-system --create-namespace -f k8s/traefik-values.yaml --wait --timeout 10m
helm upgrade --install metrics-server metrics-server/metrics-server --version "$METRICS_SERVER_CHART_VERSION" \
  -n kube-system --wait --timeout 10m
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version "$MONITORING_CHART_VERSION" \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml --wait --timeout 15m
kubectl apply -f monitoring/dashboard-configmap.yaml -f monitoring/alerts.yaml
helm upgrade --install relaydesk helm/relaydesk -n relaydesk \
  -f helm/relaydesk/values-prod.yaml -f helm/relaydesk/values-release.yaml \
  --wait --wait-for-jobs --timeout 10m
kubectl get pods,svc,ingress,hpa -n relaydesk
helm list -n relaydesk
```

Capture the Helm release, two healthy frontend/backend replicas, services and ingress.
The migration Job should be `Completed`; service pods should be `Running`/Ready.
If a pod is not ready, inspect `kubectl describe pod` and `kubectl logs` before proceeding.

For the required Argo CD demonstration, transfer ownership after capturing Helm evidence.
The StatefulSet PVC survives this Helm uninstall; do not delete it.

```bash
helm upgrade --install argocd argo/argo-cd --version "$ARGOCD_CHART_VERSION" \
  -n argocd --create-namespace -f gitops/values-demo.yaml --wait --timeout 10m
helm uninstall relaydesk -n relaydesk --wait
kubectl apply -f gitops/application.yaml
kubectl wait -n argocd application/relaydesk --for=jsonpath='{.status.sync.status}'=Synced --timeout=600s
kubectl wait -n argocd application/relaydesk --for=jsonpath='{.status.health.status}'=Healthy --timeout=600s
```

Argo renders the Helm chart but does not create a Helm CLI release. Keep the earlier
`helm list` evidence, and show Argo's Helm source, synced revision and resource tree.
Do not run `helm upgrade relaydesk` while Argo owns the application.

## 5. Open the application and live monitoring

Add `127.0.0.1 relaydesk.local` to your computer's hosts file (`sudo nano /etc/hosts`
on macOS), then run in a dedicated terminal:

```bash
bash scripts/demo-access.sh
```

Open:

- Application through ingress: http://relaydesk.local:3000
- API documentation: http://localhost:8000/docs
- Prometheus targets: http://localhost:9090/targets
- Grafana: http://localhost:3001
- Argo CD: https://localhost:8443 (the local demo uses a self-signed certificate)

Retrieve passwords in a separate terminal **before recording**. Both usernames are `admin`:

```bash
kubectl get secret monitoring-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 --decode
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 --decode
```

Sign in, then clear/close the credential terminal. In Grafana open **RelayDesk · Service
health** and select Prometheus if needed. Generate traffic and allow at least 30–60 seconds:

```bash
python3 scripts/seed.py
URL=http://relaydesk.local:3000/api/tickets REQUESTS=1000 bash scripts/load-test.sh
curl --fail http://localhost:8000/metrics
kubectl top pods -n relaydesk
kubectl get hpa -n relaydesk
```

Capture both backend targets UP, Grafana panels with real data, the application UI,
and Argo `Synced/Healthy`. Show HPA readings; do not claim a scaling event unless observed.

Capture the terminal output of `kubectl get pods -n relaydesk`,
`kubectl get svc -n relaydesk`, and `curl http://localhost:8000/metrics`, plus the
earlier `helm list -n relaydesk` output. On macOS use Shift–Command–4 to select the
terminal area. Passing pytest and both Trivy report screenshots are already
archived; capture your EKS walkthrough's terminal screenshots. The committed JSON/text reports are useful supporting evidence,
but the rubric explicitly requests these screenshots.

## 6. Record your own presentation

Use QuickTime Player → File → New Screen Recording, or your preferred recorder.
Enable your microphone. Aim for a clear 10–15 minute walkthrough; edit waiting periods
only if the demonstrated sequence remains honest. Follow [demo/RECORDING.md](../demo/RECORDING.md):

1. Present `demo/slides.pdf` first and explain the architecture.
2. Show the original application, code, migrations, tests and non-root Dockerfiles.
3. Make a small meaningful change, push it, and show its complete green CI run and SHA-tagged GHCR images.
4. Show the real Terraform plan/apply and AWS VPC/EKS evidence.
5. Show Kubernetes workloads, Helm evidence, ingress and Argo CD GitOps behavior.
6. Generate traffic and show Prometheus UP targets and populated Grafana panels.
7. Explain the security scan result, limitations and cleanup.

Your narration should explain why tests run before builds, why scans block publication,
why liveness differs from readiness, and why a clean scan is not a guarantee of zero risk.
The automated browser clips are supplementary test evidence, **not** the mandatory narrated presentation.

## 7. Clean up AWS after recording/evaluation

Capture evidence first. Follow the exact ownership and retained-volume cleanup in
[DEPLOYMENT.md §8](DEPLOYMENT.md#8-cleanup-after-evaluation). This intentionally discards
the demo database: save anything you need beforehand. Identify each retained EBS volume
from its PV's `spec.csi.volumeHandle`; delete only the matching detached demo volume.

```bash
terraform -chdir=terraform plan -destroy
terraform -chdir=terraform destroy
```

Review and confirm the destroy prompt. Capture `Destroy complete!`, then verify no demo
EKS/node groups, NAT gateways, load balancers or retained EBS volumes remain. Terraform
does not own dynamically created PVC disks. Keep the destroy screenshot for submission.

## 8. Upload the video and submit

Save your recording as `relaydesk-walkthrough.mp4`. For a large video, upload a GitHub
release asset rather than committing a large binary to Git:

```bash
gh release create capstone-demo --target main --title "RelayDesk capstone walkthrough" \
  --notes "Narrated project walkthrough and presentation slides." \
  /absolute/path/to/relaydesk-walkthrough.mp4 demo/slides.pdf
```

If that release already exists, use `gh release upload capstone-demo FILE` instead.
Update `demo/RECORDING.md` with the release URL and commit it. Add reviewed AWS screenshots
and the other required evidence under `demo/evidence/`; exclude credentials, state and
plan binaries. Capture the commit history showing at least 10 meaningful commits.

Finally, submit **https://github.com/THRISHAL12345/relaydesk** at
https://forms.gle/XWAP1vAumDJgAPM1A and retain the confirmation. The scaffold lists
“Sunday, 19 October 2026”; that date is a Monday, so confirm the intended deadline
with your instructor. Do not assume completion of CI submits the form.

## Optional: rehearse without AWS

Install Kind, Docker, kubectl, Helm, Python 3 and Node 22. From a clean pushed checkout:

```bash
export PATH="$HOME/.local/bin:$PATH"
bash scripts/local-demo.sh
bash scripts/demo-access.sh
```

Node 22 and the verified Kind binary are installed under `~/.local/bin` on the
current machine; the PATH line selects them. The current workspace already has a
running `kind-relaydesk-demo` cluster. To use it
again, select `kubectl config use-context kind-relaydesk-demo` and run
`bash scripts/demo-access.sh`; do not recreate it. For a fresh machine, the command
above creates only the dedicated `relaydesk-demo` Docker/Kind cluster, builds local
images, verifies Helm, monitoring and Argo self-heal, and leaves it running for rehearsal.
It is not AWS evidence. To discard only this local demo later:

```bash
kind delete cluster --name relaydesk-demo
```
