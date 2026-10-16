# LastBite submission checklist

Use `devsecops-python-main/GRADING.md` as the authority. Automated logs supplement screenshots; they do not replace screenshots explicitly requested by the rubric.

- [ ] Final LastBite repository URL and at least ten meaningful commits, all using the requested identity.
- [ ] Browser proof of listing creation, reservation, cancellation, code-verified pickup and responsive layout.
- [ ] Pytest terminal screenshot, with at least five cases across three API routes and a disposable database.
- [ ] Compose startup and non-root container proof.
- [ ] New successful LastBite Actions URL, SHA-tagged GHCR images, and both Trivy reports.
- [ ] Explain a scan finding or explain what a clean scan covers.
- [ ] LastBite Terraform plan, AWS Console VPC/EKS screenshots, worker group and successful cleanup output.
- [ ] LastBite pods, services, two replicas per application deployment, Helm release and ingress screenshots.
- [ ] LastBite Prometheus targets UP, `/metrics` output and populated Grafana dashboard.
- [ ] Argo CD Synced/Healthy and a demonstrated self-heal with the new repository revision.
- [ ] Present the updated ten-slide PDF, then record the complete live walkthrough with your own narration.
- [ ] Upload the video and slides when publication is authorized, then submit the instructor's form.

Historical RelayDesk evidence is retained under `demo/legacy-relaydesk/` and ignored `artifacts/aws/`. Do not submit it as if it were LastBite evidence. See [VALIDATION.md](VALIDATION.md) for the new local checks already completed.
