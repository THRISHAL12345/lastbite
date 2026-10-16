# Submission evidence checklist

Use the original GRADING.md for final scoring. This map identifies implemented files and evidence that must come from an actual run. Checked items mean files exist or local checks passed, not that AWS or GitHub deployment has happened.

| Module | Project artifacts | Evidence to capture |
|---|---|---|
| M1 Application | `backend/app`, Alembic migration, React UI, Compose | Running browser, CRUD API demo and PostgreSQL tables |
| M2 Testing | 19 API test cases; migration-backed disposable DB; frontend workflow test | `pytest -v` output and successful PostgreSQL CI job |
| M3 Git | `.gitignore`, repository-ready structure | Repository URL and genuine development history with at least 10 meaningful commits |
| M4 Docker | Non-root API and multi-stage unprivileged Nginx Dockerfiles | Both successful builds, healthy Compose services and localhost UI |
| M5 CI/CD | GitHub Actions workflow and Argo CD promotion manifest | Green run URL, SHA-tagged GHCR packages, reviewed promotion and Synced/Healthy app |
| M6 Security | Trivy scans for both images; explicit fail gate | Both reports and an explanation of a real CVE or clean scan result |
| M7 Infrastructure | Formatted Terraform, variables example, VPC/EKS/EBS CSI | Init/validate/plan, AWS console proof, apply and destroy completion |
| M8 Kubernetes | Namespace, full Helm chart, Ingress, HPA | Pods, services, Helm CLI demo, ingress access and Argo CD Helm source |
| M9 Monitoring | Metrics middleware, ServiceMonitor, alert rules, dashboard JSON | Metrics output, Prometheus Target UP and populated Grafana panels |
| M10 Presentation | README, 10-slide PDF, recording script | Actual MP4 in repo or release asset with slides-first walkthrough |

## Files and local checks

- [x] Original helpdesk domain and data model.
- [x] Create/read/update/delete, filters, search, pagination, comments and SLA calculations.
- [x] Alembic upgrade and downgrade tested on disposable SQLite.
- [x] 19 backend tests pass locally.
- [x] Frontend DOM workflow test passes; production build passes.
- [x] Compose configuration validates.
- [x] Helm default and production variants lint and render.
- [x] Terraform formatting passes.
- [x] PDF slide deck generated and rendered for inspection.

## Remaining real-environment evidence

- [ ] Start Compose and capture healthy PostgreSQL/API/UI.
- [ ] Inspect desktop and mobile rendering in a browser.
- [ ] Publish your GitHub repository and build genuine commit history.
- [ ] Run CI against PostgreSQL and obtain both Trivy reports.
- [ ] Publish GHCR images and promote their source SHA.
- [ ] Run Terraform init, validate, plan and apply with your AWS account.
- [ ] Configure your repository URL, hostname, CIDR, secret and registry visibility.
- [ ] Install the platform charts and application in EKS.
- [ ] Show Argo CD Synced/Healthy and the complete live walkthrough.
- [ ] Record Prometheus/Grafana/HPA evidence after generating traffic.
- [ ] Record the MP4 and commit/upload the presentation assets.
- [ ] Destroy infrastructure and verify retained disks are cleaned up.

Do not invent test output, cloud screenshots, ten artificial commits, a green CI URL, a clean security report or a presentation video. Record the real outcome, fix failures, then capture the evidence.
