# Observed submission evidence

The CI snapshot below comes from GitHub Actions running real PostgreSQL, Docker
Compose, Chromium and a disposable Kind Kubernetes cluster. A separately labeled
local Kind snapshot supplies the fully populated Grafana screenshot. Neither is
AWS/EKS evidence or a narrated presentation.

## Verified release

- [Successful run 38909790496](https://github.com/THRISHAL12345/relaydesk/actions/runs/38909790496)
- Source revision: `5458a53f041404022c1d9b268fc2cff3734bdac7`
- Backend image: `ghcr.io/thrishal12345/relaydesk-backend:5458a53f041404022c1d9b268fc2cff3734bdac7`
- Frontend image: `ghcr.io/thrishal12345/relaydesk-frontend:5458a53f041404022c1d9b268fc2cff3734bdac7`
- [Manifest with run metadata and SHA-256 hashes](ci-38909790496/manifest.json)
- [Actual green pipeline screenshot](github/successful-pipeline.png)

The release values pin these published images. A subsequent documentation or
promotion commit is expected to have a different Git SHA. This archive intentionally
preserves the exact source run rather than relabeling its evidence as a newer run.

## Evidence map

| Rubric area | Actual evidence |
|---|---|
| Application / Docker | [Desktop UI](ci-38909790496/compose-and-browser-evidence/desktop-queue.png), [mobile UI](ci-38909790496/compose-and-browser-evidence/mobile-queue.png), [resolved ticket](ci-38909790496/compose-and-browser-evidence/resolved-ticket.png), [Compose services](ci-38909790496/compose-and-browser-evidence/services.txt), [API smoke results](ci-38909790496/compose-and-browser-evidence/smoke.json) |
| Testing | [Passing pytest screenshot](github/pytest-postgresql.png), [19-test JUnit report](ci-38909790496/test-results/pytest.xml), [PostgreSQL test job](https://github.com/THRISHAL12345/relaydesk/actions/runs/38909790496/job/117002671202) |
| Git | [Actual GitHub history with ten meaningful commits](github/ten-commits.png); every author/committer is THRISHAL12345 |
| Security | [Backend scan](ci-38909790496/security-reports/backend-trivy.txt), [frontend scan](ci-38909790496/security-reports/frontend-trivy.txt), [backend output screenshot](github/backend-trivy-output.png), [frontend output screenshot](github/frontend-trivy-output.png) |
| Kubernetes / Helm | [Pods/services/ingress](ci-38909790496/kubernetes-evidence/resources.txt), [Helm release](ci-38909790496/kubernetes-evidence/helm-list.txt), [replica objects](ci-38909790496/kubernetes-evidence/deployments.json), [ingress/API smoke results](ci-38909790496/kubernetes-evidence/smoke.json) |
| Monitoring | [Metrics](ci-38909790496/kubernetes-evidence/metrics.txt), [both targets UP in CI](ci-38909790496/monitoring-evidence/prometheus-targets.png), [four populated Grafana panels locally](local-kind-2026-10-16/grafana-dashboard.png), [live CI API verification](ci-38909790496/monitoring-evidence/verification.json) |
| GitOps walkthrough | [Argo CD Synced/Healthy](ci-38909790496/gitops-evidence/argocd-synced-healthy.png), [drift to one replica](ci-38909790496/gitops-evidence/deployment-drift.json), [automatic repair to two](ci-38909790496/gitops-evidence/deployment-healed.json), [application state](ci-38909790496/gitops-evidence/application.json) |

The [local snapshot manifest](local-kind-2026-10-16/manifest.json) records its own
source revision, capture timestamps and hashes. The original CI Grafana screenshot
is retained unchanged: its replica panel had data while the request panels still
showed `No data` at capture time, despite a successful live instant query. The
capture check now waits for all four charts through dashboard refreshes, so this
early screenshot cannot silently pass in a later run.

The Trivy output screenshots show the unchanged CI reports in GitHub's file viewer
at archive commit `6c03ed088bb361d50b33fc4d48cd6c5bb15ad3e4`; they are screenshots
of the actual report files, not a recreated terminal or a new scan.

## Security explanation

Trivy scanned OS packages and installed application dependencies in both built
images and reported no HIGH or CRITICAL vulnerabilities at that scan's database
version. This does not rule out lower-severity or unknown vulnerabilities, so
dependencies must still be maintained and future builds rescanned. Both scans
must succeed before the exact tested images can be published under their source SHA.

## Remaining personal/cloud evidence

Follow [the complete handoff](../../docs/YOUR-NEXT-STEPS.md) to authenticate AWS,
provision and destroy the cloud resources, capture the rubric's terminal/GHCR/AWS
screenshots, record your own narrated video and submit the repository URL.
The [scorecard](../../docs/SCORECARD.md) estimates 82/100 demonstrated, with 18 points
dependent on these remaining steps and final instructor review.

To archive a later successful run without modifying this immutable snapshot:

```bash
python3 scripts/collect-evidence.py SUCCESSFUL_RUN_ID
```

The helper selects non-secret reports and screenshots, checks that the run
succeeded, and records original hashes. Inspect a new snapshot before committing it.
