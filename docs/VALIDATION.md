# Local validation record

Checked on 16 October 2026 in the supplied macOS workspace.

## Passed

- **19 backend tests** against a fresh temporary SQLite database, including actual Alembic upgrade/downgrade, CRUD, enum/string validation, search/pagination, SLA calculations, resolve/reopen semantics, comments, cascade deletion, readiness failure and metric labels.
- **1 frontend workflow test** using React and JSDOM: create a ticket, open its details, start work, add a comment, resolve, reopen, edit and delete. This checks application behavior with a mocked API; it is not a browser rendering test or full-stack integration test.
- **Vite production build**, with installed package-lock dependencies.
- **Docker Compose configuration** parsing with `docker compose config --quiet`.
- **Helm lint and render** with default and production values. Rendered resource checks verified ingress service/port references, HPA target, ServiceMonitor labels and non-root security contexts.
- **Terraform formatting/HCL parsing** using `terraform fmt -check -recursive`.
- **YAML parsing**, shell script syntax and Makefile recipe inspection.
- **10-slide PDF** generated, text inspected, pages rendered and visually reviewed.

## Not verified in this session

- Docker daemon access returned permission denied, so neither image builds nor the full PostgreSQL Compose stack ran here.
- Binding localhost ports returned `EPERM`, so browser UI inspection and live HTTP serving could not run. React rendering and interactions were tested in JSDOM instead.
- Terraform module initialization could not resolve `registry.terraform.io`. Provider/module validation, plan, apply and destroy need network access and AWS credentials. Formatting alone does not prove infrastructure will provision.
- GitHub Actions, GHCR publication, current CVE results, EKS, Argo CD, HPA and Prometheus/Grafana runtime behavior require the real deployment. No remote credentials, repository or AWS account were configured.
- The local cache provided the dependencies used for SQLite tests and the UI build. The PostgreSQL psycopg driver was not cached locally; the full dependency install and PostgreSQL integration are configured in CI and Docker but still require execution there.

CI performs PostgreSQL tests and migrations, frontend workflow testing/building, Helm linting, Terraform initialization/validation, image builds and the security gate. Failures must be resolved before promotion; local results are not a claim of a green remote pipeline.
