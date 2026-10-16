# LastBite on AWS: deployment and cleanup evidence

This was a real, temporary LastBite deployment in **ap-south-1** on 16 October 2026 UTC (17 October in India). The application images used tested source revision `178015224d2786be2f2621554e6d09beb25d01b2`. It is separate from the CI Kind demonstration and the historical RelayDesk deployment.

## Infrastructure

- [Initialization and validation](init-validate.txt) completed successfully.
- [Plan](plan.txt) / [plan output screenshot](terraform-plan-output.png): 60 resources to add.
- [Apply](apply.txt) / [apply output screenshot](terraform-apply-output.png): 60 added, zero changed or destroyed.
- [VPC Console](vpc-console.png) and [subnets Console](vpc-subnets-console.png): two public and two private subnets across two availability zones.
- [EKS Console](eks-active-console.png): `lastbite-eks` ACTIVE, Kubernetes 1.35.
- [Worker group Console](eks-nodegroup-console.png), [workers Console](eks-workers-console.png), and [nodes](nodes.txt): two Ready `m7i-flex.large` workers.

## Application and monitoring

The tested [bootstrap script](../../../scripts/aws-demo-bootstrap.sh) installed the pinned platform charts and the promoted LastBite images, using a dedicated kubeconfig. It used Helm ownership and private Traefik ingress, reached by port-forwarding to localhost; no public load balancer was provisioned.

- [Resources](resources.txt), [deployments](deployments.json), and [Helm releases](helm-list.txt): two Ready backend and two Ready frontend replicas, PostgreSQL and successful migrations.
- [Application through ingress](lastbite-ingress.png), [HTTP verification](ingress-verification.json), and [readiness](readiness.json): six fictional kitchen listings; the demo was seeded with eight collected meals and one pending reservation.
- [Metrics endpoint](metrics.txt), [two UP Prometheus targets](prometheus-targets.png), [Grafana dashboard](grafana-dashboard.png), and [live query verification](monitoring-verification.json): four populated panels with real application traffic.
- [HPA readings](hpa.txt) and [resource usage](resource-usage.txt): actual CPU readings were observed. This does not claim a scale-up event.

Argo CD synchronization and self-healing are proven separately in the [CI evidence](../README.md), not by this AWS deployment.

## Cleanup

The application and platform Helm releases were removed. The retained PostgreSQL PVC/PV and its exact EBS volume were explicitly deleted before Terraform teardown.

- [Final destroy log](destroy.txt) and [completion screenshot](terraform-destroy-output.png): the remaining 16 resources destroyed successfully. The [first attempt](destroy-first-attempt.txt) removed 44 of the original 60 resources before DNS resolution of the EC2 endpoint failed; a [first retry](destroy-dns-retry.txt) also hit that DNS failure. The final retry used the official Mumbai dual-stack endpoint via the command-scoped `AWS_ENDPOINT_URL_EC2` environment variable. No system DNS or repository provider configuration was changed. See [AWS endpoint documentation](https://docs.aws.amazon.com/ec2/latest/devguide/ec2-endpoints.html).
- [AWS Console after cleanup](eks-cleanup-console.png): no EKS clusters remain in this region.
- [Independent AWS cleanup verification](cleanup-verification.json): cluster removed, workers terminated, database and worker disks removed, VPC and network interfaces removed, NAT deleted, Elastic IP released, no load balancers in the demo VPC, control-plane logs removed, and empty Terraform state.
- The KMS key is **PendingDeletion**, with its scheduled deletion date recorded in the verification. Terraform schedules deletion; the key is not claimed to have disappeared immediately.

The live AWS demo is no longer running. Recreate it for the personal live recording, then clean it up again. No credentials, kubeconfig, Terraform state or binary plan files are included here. The output screenshots are labelled views of the actual archived logs; AWS, application and monitoring screenshots are captures of the real browser pages.
