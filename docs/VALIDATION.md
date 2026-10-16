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

## First GitHub run and security remediation

[Run 38901893181](https://github.com/THRISHAL12345/relaydesk/actions/runs/38901893181)
passed the PostgreSQL API tests and migrations, frontend test/build, Helm checks,
and Terraform initialization/validation. Both Docker images built. The frontend
security scan passed, but the backend scan blocked delivery with 62 HIGH and
2 CRITICAL findings in Debian OS packages; the Python dependencies had no
HIGH/CRITICAL findings. This run did not reach the live integration tests or publication.

The backend now uses Alpine with a separate compiler stage for the pinned
Psycopg 3.3.6 C adapter, updated for the current PostgreSQL client headers.
The final image contains the system libpq runtime and runs
as UID 10001; compilers remain in the build stage. A build-time import assertion
checks that the adapter can load libpq. This follows the
[Psycopg local installation guidance](https://www.psycopg.org/psycopg3/docs/basic/install.html#local-installation).
Both HIGH/CRITICAL security gates remain enabled, with no CVE suppressions.
Failed scans now print their reports directly in the gate's job log.

Local verification of the replacement image on 16 October 2026 passed:

- Fresh Trivy database and image scan: **0 HIGH/CRITICAL findings** across OS and Python packages.
- Compose with PostgreSQL: successful Alembic migration and healthy backend/frontend.
- Runtime users: backend UID 10001 and frontend UID 101.
- `scripts/smoke.py`: all seven live API/proxy/database/metrics checks passed.
- Real Chromium ticket lifecycle, reload persistence, and mobile layout: **1 passed**.
  The priority selector now uses the combobox's accessible name instead of an exact
  wrapping-label text match that included option text.

Local scan and smoke reports, browser screenshots, video, and trace/report files
are under ignored `artifacts/`. GitHub CI separately verifies Linux AMD64 images
before publication; local ARM64 results do not substitute for that run.

## Deployment evidence still required

- Terraform plan, apply and destroy require configured AWS credentials. Provider validation does not prove infrastructure will provision.
- EKS, Argo CD, HPA and Prometheus/Grafana runtime behavior require deployment evidence.
- A real presenter walkthrough and AWS screenshots are still required for submission.

CI performs PostgreSQL tests and migrations, frontend workflow testing/building, Helm linting, Terraform initialization/validation, image builds and the security gate. Failures must be resolved before promotion; local results are not a claim of a green remote pipeline.
