# Reference scaffold review

Reviewed all 58 text/source/configuration files under `devsecops-python-main`, including its four Markdown documents, hidden workflow files, backend, frontend, manifests, chart, Terraform and scripts. The two `.DS_Store` files are binary Finder metadata rather than project instructions and were excluded from content review. No source files in the reference were changed.

The README, GRADING and SUBMISSION documents together require an original application domain, at least five API tests, PostgreSQL migrations, non-root containers, CI tests and frontend build, SHA-tagged GHCR images, a blocking Trivy scan, real Terraform/EKS evidence, Helm/Ingress/HPA, Prometheus/Grafana, Argo CD in the video, and an eight-slide minimum deck plus a real recording.

| Finding in the reference | RelayDesk change |
|---|---|
| Root `ci-cd.yml` and active workflow describe different registries and deployment paths | One active workflow uses GHCR, SHA tags and an explicit GitOps promotion boundary |
| Active Trivy commands omit `--exit-code 1` | Both scan outcomes gate image publication |
| Images are rebuilt across isolated jobs | Build once per image, scan and push the same local images |
| Pull requests can reach registry push jobs | Registry credentials and pushes restricted to main, non-PR runs |
| Only three API tests, with shared persistent SQLite state | Isolated migration-backed tests; PostgreSQL service in CI |
| Frontend Nginx runs as root on port 80 | Unprivileged Nginx runtime on port 8080 |
| Compose has no database readiness ordering | PostgreSQL healthcheck, one-shot migration, API readiness dependency |
| API startup creates schema outside migrations | Alembic exclusively owns the application schema |
| Helm ingress references mismatched backend name/port | Release-scoped service naming and matching ports throughout |
| Backend secrets are embedded in a connection string in values | Existing Secret references and properly encoded SQLAlchemy connection URL |
| Backend lacks imagePullSecrets support | Frontend, backend and migration job all support pull secrets |
| Monitoring CRD assumed on every chart install | ServiceMonitor opt-in; documented monitoring prerequisite |
| Terraform is compressed into invalid same-line HCL attributes | Formatted HCL with example tfvars, EBS CSI identity and storage class |
| Vite proxies to 8080 while API instructions use 8000 | One development API port: 8000 |
| Activity and CI status UI use fixed data | Persisted event feed and no pretend deployment status |
| Load script targets nonexistent `/api/health` and suppresses failures | Bounded concurrent API requests with visible HTTP failures |
| Argo CD requested by the rubric but absent in scaffold | Argo CD Application, sync waves, migration hook and promotion instructions |

RelayDesk replaces task management with IT support: requester/category fields, deterministic SLA deadlines, reopen behavior, comments, audit events, queue filters and pagination. The new UI is a support workspace, with functional queue navigation and ticket detail actions.
