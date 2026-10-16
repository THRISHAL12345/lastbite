#!/usr/bin/env python3
"""Render an Argo Application for the isolated Kind demo; no credentials are included."""
import json
import os
import re

revision = os.environ['REPO_REVISION']
tag = os.environ['IMAGE_TAG']
prefix = os.environ['IMAGE_PREFIX']
if not re.fullmatch(r'[a-f0-9]{40}', revision):
    raise SystemExit('REPO_REVISION must be a full Git commit SHA')
parameters = {
    'backend.repository': prefix + '-backend', 'backend.tag': tag,
    'frontend.repository': prefix + '-frontend', 'frontend.tag': tag,
    'ingress.enabled': 'true', 'ingress.host': 'lastbite.local',
    'monitoring.enabled': 'true',
}
print(json.dumps({
    'apiVersion': 'argoproj.io/v1alpha1', 'kind': 'Application',
    'metadata': {'name': 'lastbite', 'namespace': 'argocd'},
    'spec': {
        'project': 'default',
        'source': {'repoURL': os.environ.get('REPO_URL', 'https://github.com/THRISHAL12345/lastbite.git'),
                   'targetRevision': revision, 'path': 'helm/lastbite',
                   'helm': {'releaseName': 'lastbite', 'parameters': [
                       {'name': key, 'value': value, 'forceString': key.endswith(('.tag', '.repository'))}
                       for key, value in parameters.items()]}},
        'destination': {'server': 'https://kubernetes.default.svc', 'namespace': 'lastbite'},
        'syncPolicy': {'automated': {'prune': True, 'selfHeal': True},
                       'syncOptions': ['CreateNamespace=true'], 'retry': {'limit': 3}},
    },
}, indent=2))
