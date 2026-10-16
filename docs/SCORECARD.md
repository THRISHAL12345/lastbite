# LastBite grading status

The capstone is graded against `devsecops-python-main/GRADING.md`. No new total is asserted for this conversion awaiting publication: the application's domain, APIs, images and names have changed, so old RelayDesk screenshots and CI results cannot establish a LastBite score.

| Module | LastBite evidence to validate |
|---|---|
| M1 Application / 10 | Meal listings, reservation/pickup flow, PostgreSQL migrations and responsive UI |
| M2 Tests / 10 | LastBite API tests against a disposable DB, migration lifecycle, concurrency checks and test output |
| M3 Git / 5 | Repository renamed using gh-personal and LastBite conversion committed locally; push and final form submission remain |
| M4 Docker / 10 | Rebuilt LastBite images, non-root users, healthy Compose stack and browser screenshot |
| M5 CI / 15 | A new successful remote pipeline and LastBite SHA-tagged GHCR packages |
| M6 Security / 5 | Both LastBite image scans and an explanation of the observed results |
| M7 Terraform / 15 | LastBite plan, VPC/EKS proof, worker group and clean teardown |
| M8 Kubernetes / 15 | LastBite Helm deployment, two frontend/backend replicas, services and working ingress |
| M9 Monitoring / 10 | LastBite targets UP and Grafana charts populated with LastBite traffic |
| M10 Presentation / 5 | Updated README/slides plus the mandatory personal narrated video |

See [VALIDATION.md](VALIDATION.md) for completed local checks. Remaining evidence must come from actual runs. The old scorecard is preserved under `demo/legacy-relaydesk/`; it is not the score of this version. The rubric assigns zero to M10 without the mandatory narrated video.
