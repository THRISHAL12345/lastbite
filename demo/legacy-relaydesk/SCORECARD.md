# Evidence-based grading estimate

This is a self-assessment against the supplied `devsecops-python-main/GRADING.md`,
not an instructor-awarded grade. The estimated demonstrated score is **82/100**.
The evidence index is [demo/evidence/README.md](../demo/evidence/README.md).

| Module | Estimate | Basis / remaining requirement |
|---|---:|---|
| M1 Application | 10/10 | PostgreSQL migrations, REST lifecycle, responsive React UI and real browser checks |
| M2 Testing | 10/10 | 19 API tests against a disposable database; PostgreSQL CI and migration checks |
| M3 Git/GitHub | 3/5 | Public repository, ten meaningful commits and ignore rules; submission-form confirmation still needed for 2 points |
| M4 Docker | 10/10 | Both images build; multi-stage frontend; non-root runtime; healthy Compose stack |
| M5 CI/CD | 15/15 | Tests gate builds, both images published to GHCR under the full source SHA |
| M6 Security | 5/5 | Both Trivy scans, enforced HIGH/CRITICAL gate and written explanation; be prepared to explain it yourself |
| M7 Terraform/AWS | 4/15 | Valid HCL (2), successful init (1), tfvars example (1); cloud execution remains |
| M8 Kubernetes/Helm | 15/15 | Actual namespace apply, Helm installation, two replicas each, ClusterIP services and tested ingress routes |
| M9 Observability | 10/10 | Real metrics, both targets UP, accessible Grafana and populated charts |
| M10 Presentation/docs | 0/5 | README and 10-slide PDF exist, but the rubric awards zero without the mandatory narrated video |
| **Total** | **82/100** | **18 points depend on the remaining user steps** |

M8/M9 were demonstrated in real Kubernetes using Kind. These are not AWS/EKS
results. The grader may require the same evidence from EKS during the complete
walkthrough; reproduce it there using the handoff guide. Complete every requested
screenshot as well as the functional criteria: JSON/text logs supplement, rather
than replace, an explicitly requested screenshot.

## Remaining path to 100

- **11 infrastructure points:** error-free non-empty plan (2), provisioned VPC with
  two public subnets (3), EKS with a worker group (4), clean destroy (2).
- **5 presentation points:** record your own slides-first narrated full walkthrough,
  upload it to this repository/release, and keep the existing README/slides accessible.
- **2 submission points:** submit the public repository in the official form and
  retain confirmation.

Follow [YOUR-NEXT-STEPS.md](YOUR-NEXT-STEPS.md) in order. Only completed, observed
results should be added to this scorecard. A successful Terraform validate does
not count as plan/apply, and an automated browser clip does not count as narration.
