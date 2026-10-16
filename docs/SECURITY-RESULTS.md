# LastBite container security results

The [successful CI run](https://github.com/THRISHAL12345/lastbite/actions/runs/38944319489) scanned both Linux AMD64 images for source revision `178015224d2786be2f2621554e6d09beb25d01b2` with Trivy. Both reports contain zero HIGH or CRITICAL vulnerabilities among the detected operating-system and application packages at scan time. This is a time-specific dependency/container result, not proof that the application has no security defects; application authorization, configuration, and newly disclosed vulnerabilities require separate assessment.

The workflow uses severity `HIGH,CRITICAL` and exit code `1`. Both scan outcomes must be successful before publication; `continue-on-error` on each individual scan allows collecting both reports, and the explicit enforcement step fails the job if either scan failed. No CVE exclusions or `ignore-unfixed` bypasses are configured.

- [Backend report](../demo/evidence/ci-38944319489/security-reports/backend-trivy.txt)
- [Frontend report](../demo/evidence/ci-38944319489/security-reports/frontend-trivy.txt)
- [Workflow](../.github/workflows/ci-cd.yml)

For the presentation, explain these results in your own words. A clean scan does not compensate for this classroom application's lack of authentication and customer isolation, which is documented in the README.
