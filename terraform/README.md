# LastBite AWS infrastructure

This module provisions a two-AZ VPC, public/private subnets, a single NAT gateway, EKS 1.35, two managed worker nodes, control-plane logs and an EBS CSI IAM role/add-on. `k8s/storageclass.yaml` creates encrypted gp3 volumes after the cluster is ready.

```bash
cp terraform.tfvars.example terraform.tfvars
# Set your own administrator public IP /32 in admin_cidrs.
terraform init
terraform fmt -check
terraform validate
terraform plan -out=deployment.tfplan
terraform apply deployment.tfplan
```

Use an AWS profile or SSO. Never commit credentials, plan files, state or tfvars. Commit `.terraform.lock.hcl` after initialization. Configure an encrypted remote backend with locking for shared work; none is created automatically here. Kubernetes platform add-ons are installed separately as described in [the deployment runbook](../docs/DEPLOYMENT.md).

The example address in tfvars is a documentation-only placeholder. Region defaults to `ap-south-1`; two AZs are selected dynamically. Change the region, node type, cluster version and CIDRs deliberately and review the resulting plan. AWS capacity and permissions can affect provisioning.

EKS, nodes, NAT gateways, logs and EBS incur costs. Remove the workloads, handle retained PV/EBS data explicitly, then run `terraform plan -destroy` and `terraform destroy` after evaluation. Terraform does not own volumes dynamically created through Kubernetes PVCs. Follow the runbook's cleanup order and verify no resources remain unexpectedly.
