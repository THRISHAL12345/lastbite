# LastBite evidence index

The [successful CI run](https://github.com/THRISHAL12345/lastbite/actions/runs/38944319489) tested source revision `178015224d2786be2f2621554e6d09beb25d01b2`. Its selected artifacts are archived in [ci-38944319489](ci-38944319489/manifest.json), with source URLs, job outcomes, and SHA-256 file hashes. This CI environment is a disposable Kind cluster, not AWS.

| Rubric module | Evidence |
|---|---|
| M1 Application | [Desktop marketplace](ci-38944319489/compose-and-browser-evidence/desktop-marketplace.png), [mobile](ci-38944319489/compose-and-browser-evidence/mobile-marketplace.png), [pickup](ci-38944319489/compose-and-browser-evidence/pickup-confirmed.png), [API smoke](ci-38944319489/compose-and-browser-evidence/smoke.json) |
| M2 Tests | [32 passing PostgreSQL tests](ci-38944319489/test-results/pytest.xml), [output screenshot](github/pytest-output.png) |
| M3 Git | [Public repository and history](https://github.com/THRISHAL12345/lastbite/commits/main/), [history screenshot](github/commit-history.png); the owner reports the submission form is complete |
| M4 Docker | [Compose services](ci-38944319489/compose-and-browser-evidence/services.txt), [startup screenshot](github/compose-output.png); the successful CI includes both image builds and non-root checks |
| M5 CI/CD | [Green run screenshot](github/successful-pipeline.png); [backend SHA tag](github/backend-ghcr.png), [frontend SHA tag](github/frontend-ghcr.png), [anonymous manifest verification](github/registry-verification.json) |
| M6 Security | [Scan explanation](../../docs/SECURITY-RESULTS.md), [backend](ci-38944319489/security-reports/backend-trivy.txt), [frontend](ci-38944319489/security-reports/frontend-trivy.txt) |
| M7 Terraform/AWS | [Plan](aws/plan.txt), [apply](aws/apply.txt), [VPC](aws/vpc-console.png), [two public/two private subnets](aws/vpc-subnets-console.png), [active EKS](aws/eks-active-console.png), [active worker group](aws/eks-nodegroup-console.png), [destroy screenshot](aws/terraform-destroy-output.png), [cleanup verification](aws/cleanup-verification.json) |
| M8 Kubernetes | [Pods/services/ingress](ci-38944319489/kubernetes-evidence/resources.txt), [two ready replicas each](ci-38944319489/kubernetes-evidence/deployments.json), [Helm release](ci-38944319489/kubernetes-evidence/helm-list.txt), [ingress smoke](ci-38944319489/kubernetes-evidence/smoke.json) |
| M9 Monitoring | [Metrics](ci-38944319489/kubernetes-evidence/metrics.txt), [Prometheus targets](ci-38944319489/monitoring-evidence/prometheus-targets.png), [Grafana](ci-38944319489/monitoring-evidence/grafana-dashboard.png), [live query verification](ci-38944319489/monitoring-evidence/verification.json) |
| GitOps walkthrough | [Argo CD](ci-38944319489/gitops-evidence/argocd-synced-healthy.png), [application](ci-38944319489/gitops-evidence/application.json), [intentional drift](ci-38944319489/gitops-evidence/deployment-drift.json), [automatic repair](ci-38944319489/gitops-evidence/deployment-healed.json) |
| M10 Presentation | [Ten-slide deck](../slides.pdf), [recording guide](../RECORDING.md); personal narrated video remains pending |

Historical RelayDesk evidence under `demo/legacy-relaydesk` is not relabelled as LastBite proof. Logs supplement the screenshots required by the rubric. The final video must include a live walkthrough; archived CI browser clips alone do not satisfy it.

## Screenshot sources

[GitHub screenshots](github/) show the green workflow, full-SHA packages, and commit history. The `*-output.png` images are browser-rendered views of actual archived command output, clearly labelled as archived rather than live terminals; the accompanying text/XML/report files and original run provide provenance. They contain no invented output. [AWS Console screenshots](aws/) show the separate LastBite VPC; the Terraform plan is saved beside them.

## Additional AWS runtime proof

The [AWS deployment record](aws/README.md) includes the LastBite ingress, two application replicas each, Prometheus targets and all four Grafana panels. The temporary deployment was removed after capture; the destroy log and independent AWS cleanup checks are archived beside the provisioning proof.
