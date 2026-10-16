#!/usr/bin/env python3
"""Verify real scrape targets, positive traffic and Grafana's configured data source."""
import base64
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

OUTPUT = Path('artifacts/monitoring')
OUTPUT.mkdir(parents=True, exist_ok=True)


def fetch(url, auth=None):
    headers = {'Authorization': auth} if auth else {}
    with urlopen(Request(url, headers=headers), timeout=10) as response:
        return json.load(response)


secret = json.loads(subprocess.check_output([
    'kubectl', 'get', 'secret', 'monitoring-grafana', '-n', 'monitoring', '-o', 'json']))['data']
username = base64.b64decode(secret['admin-user']).decode()
password = base64.b64decode(secret['admin-password']).decode()
auth = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
query = 'sum(rate(lastbite_http_requests_total{namespace="lastbite"}[5m]))'
deadline = time.monotonic() + 240
last_error = None
while time.monotonic() < deadline:
    try:
        # Keep real traffic flowing across at least two Prometheus scrapes.
        for _ in range(20):
            fetch('http://127.0.0.1:8100/api/listings?limit=1')
        targets = fetch('http://127.0.0.1:9090/api/v1/targets')['data']['activeTargets']
        targets = [t for t in targets if t['labels'].get('namespace') == 'lastbite'
                   and t['labels'].get('service') == 'lastbite-backend']
        assert len(targets) == 2 and all(t['health'] == 'up' for t in targets), 'Both backend targets must be UP'
        result = fetch('http://127.0.0.1:9090/api/v1/query?' + urlencode({'query': query}))
        assert result['data']['result'] and float(result['data']['result'][0]['value'][1]) > 0, 'Need positive request rate'
        dashboard = fetch('http://127.0.0.1:3001/api/dashboards/uid/lastbite-health', auth)
        sources = fetch('http://127.0.0.1:3001/api/datasources', auth)
        source = next(s for s in sources if s['type'] == 'prometheus' and s['isDefault'])
        grafana = fetch(f"http://127.0.0.1:3001/api/datasources/proxy/uid/{source['uid']}/api/v1/query?" + urlencode({'query': query}), auth)
        assert float(grafana['data']['result'][0]['value'][1]) > 0, 'Grafana data source must return live traffic'
        # Verify every chart's range query, not just an instant request counter.
        # A new cluster needs multiple scrapes before rates and latency exist.
        panels = dashboard['dashboard']['panels']
        assert len(panels) == 4, 'Expected all four service-health panels'
        end = int(time.time())
        panel_results = []
        for panel in panels:
            for target in panel['targets']:
                params = {'query': target['expr'], 'start': end - 900, 'end': end, 'step': 15}
                data = fetch(f"http://127.0.0.1:3001/api/datasources/proxy/uid/{source['uid']}/api/v1/query_range?" + urlencode(params), auth)
                series = data.get('data', {}).get('result', [])
                assert data.get('status') == 'success' and any(
                    sum(math.isfinite(float(value)) for _, value in item.get('values', [])) >= 2
                    for item in series
                ), f"Panel {panel['title']} needs at least two finite samples"
                panel_results.append({'id': panel['id'], 'title': panel['title'],
                                      'query': target['expr'], 'result': data})
        evidence = {'checked_at': datetime.now(timezone.utc).isoformat(), 'passed': True,
                    'backend_targets': targets, 'prometheus_query': result, 'grafana_query': grafana,
                    'dashboard_uid': dashboard['dashboard']['uid'],
                    'datasource_uid': source['uid'], 'panels': panel_results}
        (OUTPUT / 'verification.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print('PASS: two UP backend targets, positive request rate, and live data for all four Grafana panels.')
        break
    except Exception as error:
        last_error = str(error)
        print(f'Waiting for monitoring: {last_error}', flush=True)
        time.sleep(5)
else:
    raise SystemExit(f'Monitoring verification failed: {last_error}')
