# LastBite validation record

Checked locally on 16 October 2026 after replacing the RelayDesk application. After validation, the owner authorized renaming the repository and committing: `gh-personal` selected `THRISHAL12345`, the repository was renamed to `THRISHAL12345/lastbite`, and the conversion was committed locally under that identity. No GitHub push or AWS creation was performed.

## Passed for this version

- **32 API tests on a fresh SQLite database**, including actual Alembic upgrade/downgrade, listing CRUD, search, filters, validation, atomic reservations, concurrent last-box contention, concurrent cancellation, code matching, time-window rules, expiry, stock editing, retained history, readiness failure and bounded metric labels.
- **The same 32 tests on a separate PostgreSQL 16 database.** Eight concurrent customers competing for three boxes produced exactly three reservations; two simultaneous cancellations restored stock only once. The disposable test container was stopped and removed afterwards.
- **5 frontend tests** covering readable API error handling, validation errors, empty DELETE responses, countdown boundaries and writable-field filtering.
- **Vite production build** and both rebuilt Docker images.
- **Healthy Compose deployment** with PostgreSQL, a completed migration service, non-root backend UID 10001, and non-root frontend UID 101. The running local demo uses frontend port 3002 and backend port 8002.
- **Live API smoke checks:** listing CRUD/search through the Nginx proxy, reservation stock accounting, oversell rejection, cancellation, pickup-code validation, duplicate-pickup rejection, impact totals, history protection and Prometheus metrics.
- **2 real Chromium browser tests:** publish/edit/delete listings; reserve/cancel/re-reserve; persist across reload; reject an incorrect code; confirm pickup; edit stock; and navigate mobile with no horizontal overflow at 390px. A rotated SVG overflow found by the first run was fixed before the final passing run.
- **Trivy local ARM64 image scans:** zero HIGH or CRITICAL findings for both LastBite backend and frontend. Both severity gates remain enforced; no exceptions were added. These findings describe the scanned images and database at this time, not future builds or unscanned architectures.
- **Helm lint and production chart rendering**, **Terraform formatting and validation**, Compose configuration parsing, Python/shell syntax, dashboard JSON, and Git whitespace checks for text files.
- **Updated ten-slide PDF**, rendered and visually inspected. It covers the LastBite workflow and delivery architecture; it does not claim a new AWS deployment.

Logs and reports are under ignored `artifacts/lastbite/`. Browser test screenshots/video are in `artifacts/browser/`. The clean demo has six fictional kitchens, eight collected sample meals and one pending reservation. Test-created kitchen records were removed after validation; saved test evidence remains intact.

## Not yet demonstrated for LastBite

- A new GitHub Actions run and LastBite GHCR image publication.
- LastBite deployed through Helm/Argo CD on Kubernetes, its HPA readings, Prometheus targets and live Grafana panels.
- LastBite Terraform plan/apply on AWS, Console screenshots, or a LastBite cloud teardown.
- A personal narrated presentation and submission-form confirmation.

The historical RelayDesk evidence is preserved under `demo/legacy-relaydesk/` and ignored `artifacts/aws/`. Its earlier AWS demo was destroyed. Those historical results are not relabelled as LastBite validation. `values-release.yaml` remains explicitly unpromoted until a real LastBite build passes CI and publishes.
