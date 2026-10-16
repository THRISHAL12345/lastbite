# Final walkthrough recording

The real MP4 is still to be recorded after deployment. This file is a recording plan, not video evidence. Upload the video under `demo/` or as a GitHub release asset and link it here. Large recordings can use a release asset or Git LFS according to instructor rules.

Suggested order (about 10-15 minutes):

1. Present all ten pages of `slides.pdf`. Explain the helpdesk domain, architecture, delivery gates and limits.
2. Show the codebase: models, SLA calculations, migration, tests, Dockerfiles and Helm values. Explain why readiness depends on the database while liveness does not.
3. Create a ticket in the UI, assign it, start work, add a note, resolve and reopen it. Show search, filters and the API documentation. Explain the continuous-hours SLA policy.
4. Make a small real source change, commit it and push. Show PostgreSQL tests, UI build, image builds, both Trivy reports, successful publication and matching SHA tags in GHCR.
5. Show Terraform plan/apply output and the actual VPC, subnets, EKS cluster and worker nodes in the correct AWS account and region. Keep credential values off screen.
6. Promote the successful source SHA in a reviewed values commit. Show Argo CD moving to Synced/Healthy, its Helm configuration, PostgreSQL readiness and migration order.
7. Show `kubectl get pods,svc,ingress,hpa -n relaydesk`. Explain why an Argo-rendered chart is not a Helm CLI release; capture direct Helm evidence separately if required.
8. Generate traffic. Show Prometheus Targets with the backend UP and populated Grafana request/latency panels. Show HPA metrics without claiming a scaling event that did not occur.
9. Apply an isolated troubleshooting manifest, inspect the failure, describe the root cause, then delete the lab resource. Show the main application still works.
10. Explain limitations, lessons and cleanup. Capture Terraform destroy completion and verify retained EBS volumes are deliberately cleaned up.

Rebuild the slide PDF if you change the implementation:

```bash
python3 -m pip install reportlab
python3 demo/build_slides.py
```

Add real recording location here when complete: **Pending**.
