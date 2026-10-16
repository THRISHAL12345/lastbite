#!/usr/bin/env bash
# Read-only AWS identity check and local Terraform preparation; never applies infrastructure.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${AWS_PROFILE:?Set AWS_PROFILE to your configured profile, e.g. lastbite}"
export AWS_REGION="${AWS_REGION:-ap-south-1}"
export AWS_PAGER=""
aws sts get-caller-identity
echo "Profile: $AWS_PROFILE | Region: $AWS_REGION"
if [[ ! -f terraform/terraform.tfvars ]]; then
  export LASTBITE_ADMIN_IP="${LASTBITE_ADMIN_IP:-$(curl --fail --silent --show-error --max-time 15 https://checkip.amazonaws.com)}"
  python3 - <<'PY'
import ipaddress, os
from pathlib import Path
ip = ipaddress.ip_address(os.environ['LASTBITE_ADMIN_IP'].strip())
if ip.version != 4 or not ip.is_global:
    raise SystemExit('Set LASTBITE_ADMIN_IP to your real public IPv4 address.')
source = Path('terraform/terraform.tfvars.example').read_text()
source = source.replace('203.0.113.10/32', f'{ip}/32')
source = source.replace('"ap-south-1"', '"' + os.environ['AWS_REGION'] + '"')
Path('terraform/terraform.tfvars').write_text(source)
print('Created ignored terraform/terraform.tfvars with your administrator IP.')
PY
else
  echo 'Using existing terraform/terraform.tfvars; check its region and admin_cidrs before planning.'
fi
terraform -chdir=terraform init -lockfile=readonly
terraform -chdir=terraform validate
echo 'Preflight complete. Review the printed AWS account, then follow docs/YOUR-NEXT-STEPS.md.'
