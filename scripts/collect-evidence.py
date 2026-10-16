#!/usr/bin/env python3
"""Archive selected real artifacts from one successful CI run for submission review."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('run_id', type=int)
args = parser.parse_args()
repo = 'THRISHAL12345/relaydesk'
root = Path(__file__).resolve().parents[1]
run = json.loads(subprocess.check_output([
    'gh', 'run', 'view', str(args.run_id), '--repo', repo, '--json',
    'status,conclusion,headSha,url,createdAt,updatedAt,jobs'], text=True))
if run['status'] != 'completed' or run['conclusion'] != 'success':
    raise SystemExit('Only a completed successful run can become the submission evidence snapshot.')
cache = root / 'artifacts' / f'evidence-download-{args.run_id}'
destination = root / 'demo' / 'evidence' / f'ci-{args.run_id}'
if destination.exists():
    raise SystemExit(f'{destination} already exists; keep the immutable snapshot or choose another run.')
cache.mkdir(parents=True, exist_ok=True)
artifacts = {
    'test-results': ['pytest.xml'],
    'security-reports': ['backend-trivy.txt', 'frontend-trivy.txt'],
    'kubernetes-evidence': ['resources.txt', 'helm-list.txt', 'deployments.json', 'smoke.json', 'metrics.txt'],
    'monitoring-evidence': ['verification.json', 'resources.txt', 'helm-list.txt', 'servicemonitor.yaml',
                            'grafana-dashboard.png', 'prometheus-targets.png'],
    'gitops-evidence': ['application.json', 'deployment-drift.json', 'deployment-healed.json',
                       'smoke.json', 'resources.txt', 'argocd-synced-healthy.png'],
    'compose-and-browser-evidence': ['smoke.json', 'compose/services.txt',
                                   '**/desktop-queue.png', '**/mobile-queue.png', '**/resolved-ticket.png'],
}
selected = []
for artifact, patterns in artifacts.items():
    location = cache / artifact
    if not location.exists():
        subprocess.run(['gh', 'run', 'download', str(args.run_id), '--repo', repo,
                        '--name', artifact, '--dir', str(location)], check=True)
    for pattern in patterns:
        matches = list(location.glob(pattern))
        if len(matches) != 1 or not matches[0].is_file():
            raise SystemExit(f'Expected exactly one {artifact}/{pattern}; found {len(matches)}')
        selected.append((matches[0], Path(artifact) / matches[0].name))

for source, relative in selected:
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
run['archived_at'] = datetime.now(timezone.utc).isoformat()
run['environment'] = 'GitHub Actions disposable Kind cluster; not AWS/EKS evidence'
run['files'] = [{'path': str(relative), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
                for source, relative in selected]
(destination / 'manifest.json').write_text(json.dumps(run, indent=2) + '\n')
print(f'Archived {len(selected)} observed artifacts from {run["url"]} to {destination.relative_to(root)}')
print('Review the selected evidence before committing. This does not produce a narrated presentation or AWS evidence.')
