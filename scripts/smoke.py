#!/usr/bin/env python3
"""Exercise a running demo stack and write evidence only for observed responses."""
import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import uuid


INGRESS_HOST = None


def request(url, method="GET", body=None, expected=200):
    req = Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                  headers={"Content-Type": "application/json", **({"Host": INGRESS_HOST} if INGRESS_HOST else {})})
    try:
        response = urlopen(req, timeout=15)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read().decode()
        if response.status != expected:
            raise AssertionError(f"{method} {url}: expected {expected}, got {response.status}: {raw[:300]}")
        return json.loads(raw) if raw and "json" in response.headers.get("Content-Type", "") else raw


def run(frontend_url, backend_url):
    checks = []
    front, back = frontend_url.rstrip("/"), backend_url.rstrip("/")
    assert request(back + "/health") == {"status": "UP"}
    assert request(back + "/ready") == {"status": "READY"}
    checks.append("API liveness and database readiness")
    assert '<div id="root">' in request(front + "/")
    checks.append("Frontend HTML served")
    title = "Smoke test " + uuid.uuid4().hex[:12]
    payload = {"title": title, "requester": "Automated demo test", "priority": "URGENT", "category": "NETWORK", "assignee": "Smoke test", "status": "OPEN", "description": "Disposable test record; removed by smoke.py."}
    ticket = request(front + "/api/tickets", "POST", payload, 201)
    path = front + f"/api/tickets/{ticket['id']}"
    try:
        assert ticket['title'] == title and not ticket['overdue']
        assert datetime.fromisoformat(ticket['due_at'].replace('Z', '+00:00')) - datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00')) == timedelta(hours=4)
        assert request(path)['id'] == ticket['id']
        checks.append("Create/read through frontend proxy and four-hour SLA")
        page = request(front + "/api/tickets?q=" + title.replace(' ', '%20'))
        assert any(item['id'] == ticket['id'] for item in page['items'])
        assert request(front + "/api/tickets/stats")['total'] >= 1
        checks.append("Search and statistics")
        updated = request(path, "PUT", {**payload, "status": "IN_PROGRESS"})
        assert updated['status'] == 'IN_PROGRESS'
        assert request(path + '/comments', 'POST', {'message': 'Test note'}, 201)['kind'] == 'COMMENT'
        assert len(request(path + '/events')) >= 3
        resolved = request(path, 'PUT', {**payload, 'status': 'RESOLVED'})
        assert resolved['resolved_at'] and not resolved['overdue']
        reopened = request(path, 'PUT', payload)
        assert reopened['resolved_at'] is None and reopened['due_at'] == ticket['due_at']
        checks.append("Update, comment, resolution and reopening")
        metrics = request(back + '/metrics')
        assert 'relaydesk_http_requests_total' in metrics
        assert 'route="/api/tickets/{ticket_id}"' in metrics
        checks.append("Prometheus metrics with bounded route labels")
    finally:
        request(path, 'DELETE', expected=204)
    request(path, expected=404)
    checks.append("Delete and subsequent 404")
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frontend-url', default='http://127.0.0.1:3000')
    parser.add_argument('--backend-url', default='http://127.0.0.1:8000')
    parser.add_argument('--host', help='Optional HTTP Host header for an ingress port-forward')
    parser.add_argument('--output', default='artifacts/smoke.json')
    args = parser.parse_args()
    global INGRESS_HOST
    INGRESS_HOST = args.host
    result = {'started_at': datetime.now(timezone.utc).isoformat(), 'frontend_url': args.frontend_url, 'backend_url': args.backend_url}
    try:
        result['checks'] = run(args.frontend_url, args.backend_url)
        result['passed'] = True
    except Exception as error:
        result.update(passed=False, error=str(error))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
