# LastBite validation record

Checked locally on 16 October 2026 after replacing the RelayDesk application. After validation, the owner authorized renaming the repository and committing: `gh-personal` selected `THRISHAL12345`, the repository was renamed to `THRISHAL12345/lastbite`, and the conversion was committed locally under that identity. Those initial checks preceded publication. The updates below record subsequent validation separately.

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

## Verified after publication

[Run 38944319489](https://github.com/THRISHAL12345/lastbite/actions/runs/38944319489), for revision `178015224d2786be2f2621554e6d09beb25d01b2`, passed every job. It proved both AMD64 image scans, non-root Compose services, PostgreSQL/browser tests, two ready backend and frontend replicas on Kind, real ingress routing, two UP Prometheus targets, four populated Grafana panels, Argo CD Synced/Healthy, automatic drift repair, and both SHA-tagged GHCR pushes. Anonymous pulls of both published manifests were verified. See the [evidence index](../demo/evidence/README.md).

The owner reports the instructor's submission form is complete. The security results now have a [written explanation](SECURITY-RESULTS.md). Release values pin the tested revision.

## Verified on AWS

On 16 October 2026 UTC (17 October in India), Terraform provisioned 60 resources for `lastbite-eks` in `ap-south-1`: a VPC, two public and two private subnets, EKS 1.35, two managed worker nodes, and supporting resources. The promoted images ran with two Ready replicas for each application deployment, a working PostgreSQL database, private ingress, two UP Prometheus targets, and four populated Grafana panels. The [AWS evidence](../demo/evidence/aws/README.md) contains Console, app and monitoring screenshots plus actual command output.

The application, platform releases and retained database volume were removed. The first Terraform destroy removed 44 resources before an EC2 hostname DNS failure; retrying against AWS's official alternate endpoint removed the remaining 16. Independent AWS checks confirmed the cluster, workers, disks, VPC, NAT, Elastic IP, interfaces and logs were removed, no demo load balancers remained, and Terraform state was empty. The KMS key is scheduled for deletion on 16 November 2026 India time. The original attempts and successful completion are preserved, rather than hiding the recovery.

## Remaining presentation work

The personal narrated video is still required. Capture native pytest/Compose terminal screenshots during the recording if the instructor requires that exact format; the current command-output screenshots show genuine archived output in browser views. HPA readings were observed, but no scale-up event is claimed.

The historical RelayDesk evidence is preserved under `demo/legacy-relaydesk/` and ignored `artifacts/aws/`. Its earlier AWS demo was destroyed. Those historical results are not relabelled as LastBite validation. `values-release.yaml` now pins the successful LastBite build listed above.
