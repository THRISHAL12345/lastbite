# LastBite grading status

**Estimated readiness: 95/100.** This is a rubric-based estimate, not an awarded grade. The instructor decides the final score. The mandatory personal narrated video is still missing, so M10 remains **0/5** even though the README and ten-slide PDF are complete.

| Module | Estimate | Evidence |
|---|---:|---|
| M1 Application | 10/10 | Meal listing CRUD, reservations and code-verified pickups, PostgreSQL migrations, responsive React UI |
| M2 Tests | 10/10 | 32 passing PostgreSQL API tests in CI; isolated database and migration/concurrency coverage |
| M3 Git | 5/5 | Public repository, meaningful commit history, correct ignore rules; owner reports form submitted |
| M4 Docker | 10/10 | Both images built, multi-stage frontend, non-root containers, healthy Compose services |
| M5 CI/CD | 15/15 | Successful main workflow, test/build gates, both full-SHA images published to GHCR |
| M6 Security | 5/5 | Both image scans, enforced HIGH/CRITICAL gates, written clean-scan explanation |
| M7 Terraform | 15/15 | Real LastBite VPC, four subnets, EKS and managed workers, successful apply and verified teardown |
| M8 Kubernetes | 15/15 | Helm installation, two ready replicas per application, ClusterIP services and working ingress |
| M9 Monitoring | 10/10 | Metrics endpoint, two UP targets, four populated Grafana panels |
| M10 Presentation | 0/5 | README and slides prepared; personal narrated video pending |
| **Total** | **95/100** | **Record and upload the required walkthrough to complete the remaining module** |

The [evidence index](../demo/evidence/README.md) links the actual runs, screenshots and reports. [AWS validation and cleanup](../demo/evidence/aws/README.md) are separate from the CI Kind cluster. Historical RelayDesk evidence is not counted as LastBite proof.

The output screenshots display archived, genuine command output in a browser; they are explicitly labelled and accompanied by the original logs. The rubric asks for terminal screenshots for pytest and Compose: show those commands in your terminal during the live recording and save native screenshots if the instructor requires that exact format. This format distinction and the instructor's assessment can affect the estimate.

To target 100, follow [the three remaining steps](YOUR-NEXT-STEPS.md). Explain the security result in your own words and show the required live CI, AWS, GitOps, Kubernetes and monitoring walkthrough. A prepared script or an automated browser clip does not replace your narration. Form submission is user-reported; verify that its URL is the renamed LastBite repository.
