# LastBite submission checklist

Use `devsecops-python-main/GRADING.md` as the authority. See the [evidence index](../demo/evidence/README.md) for the actual proof.

- [x] Public LastBite repository and more than ten meaningful commits under the requested identity.
- [x] Owner reports the instructor's submission form is complete.
- [x] Browser proof and tests of listing creation, reservation, cancellation, code-verified pickup and responsive layout.
- [x] 32 passing PostgreSQL API tests, isolated database, archived output and output screenshot.
- [x] Compose startup and non-root container proof.
- [x] Successful LastBite Actions URL, SHA-tagged GHCR images, and both Trivy reports.
- [x] Written explanation of what the clean security scans cover.
- [x] LastBite Terraform plan/apply, AWS Console VPC/EKS screenshots, worker group and verified cleanup.
- [x] Pods/services, two ready replicas per application deployment, Helm release and working ingress.
- [x] Prometheus targets UP, `/metrics` output and four populated Grafana panels, including the AWS deployment.
- [x] Argo CD Synced/Healthy and demonstrated automatic drift repair in the CI Kind cluster.
- [x] Complete README and ten-slide PDF committed.
- [ ] Present the slides, then record the full live walkthrough with your own narration, including the security explanation.
- [ ] Capture native pytest and Compose terminal screenshots during recording if strict screenshot-format compliance is required; the current output screenshots are browser-rendered archived logs.
- [ ] Upload the narrated video to `demo/` or a GitHub release and link it from the README.
- [ ] Confirm the submitted form points to `https://github.com/THRISHAL12345/lastbite`.

The AWS demo was temporary and has been removed after evidence collection. Recreate it for the live recording, then remove it again. Historical RelayDesk evidence is retained under `demo/legacy-relaydesk/`; it is not LastBite proof.
