# LastBite recording guide

Present `slides.pdf` first, then show the live workflow. Use fictional kitchens and customers. Record your own explanation; automated browser clips do not satisfy the mandatory narrated presentation.

1. Explain restaurant management and the surplus-food problem. Describe meal listings, stock reservations and code-verified pickup.
2. In Kitchen desk, publish five meal boxes with a pickup window that is open now. Explore boxes, reserve two, and show three remaining. Cancel and show stock restored. Reserve again, enter the pickup code, and show meals rescued increasing only after collection.
3. Show category/dietary filters, search, an expired listing and mobile layout. Explain that shared demo users see all reservations and that no online payment occurs.
4. Show models, migration `0002_lastbite`, integer-paise prices, conditional stock updates, row locks, duplicate-cancellation guards, and disposable-database tests. Explain the preserved legacy migration.
5. After publication is authorized, make a real LastBite commit using `gh-personal` and THRISHAL12345; show the new pipeline, test gates, both image scans and full-SHA GHCR tags.
6. Show Terraform plan/apply output and actual AWS Console VPC/EKS proof. Show LastBite pods, two replicas, Services, Ingress and Helm configuration.
7. Show Argo CD Synced/Healthy on a LastBite revision. Change frontend replicas to one and show automatic repair. Explain why the HPA owns backend replicas.
8. Show Prometheus targets UP and Grafana request/latency/error/replica charts populated by real LastBite traffic. Inspect HPA readings; do not claim a scaling event unless observed.
9. Run the isolated broken-image/service-selector lab and explain the diagnosis.
10. Remove application data volumes and cloud resources using the deployment cleanup guide. Capture completion and verify no billed demo resources remain.

The ten-slide deck describes the architecture and demonstration plan. It does not claim a new remote CI run or AWS deployment occurred. Capture those for LastBite after publication. Never display passwords or access keys in the recording.
