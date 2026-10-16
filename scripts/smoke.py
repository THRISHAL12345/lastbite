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
    assert '<div id="root">' in request(front + "/")
    checks.append("Frontend, API liveness and migrated database readiness")
    title = "Smoke box " + uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc)
    payload = {"title": title, "restaurant": "Automated demo kitchen", "address": "Fictional test address",
               "price_paise": 9900, "original_price_paise": 29900, "quantity_total": 2,
               "pickup_start": (now-timedelta(minutes=1)).isoformat(), "pickup_end": (now+timedelta(hours=1)).isoformat()}
    item = request(front + "/api/listings", "POST", payload, 201)
    path = front + f"/api/listings/{item['id']}"
    assert request(path)['quantity_available'] == 2
    assert request(front + "/api/listings?q=" + title.replace(' ', '%20'))['total'] == 1
    request(path, "PUT", {**payload, "title": title + " updated"})
    request(path, "DELETE", expected=204)
    request(path, expected=404)
    checks.append("Listing create/read/update/delete and search through frontend proxy")
    item = request(front + "/api/listings", "POST", payload, 201)
    path = front + f"/api/listings/{item['id']}"
    reservation = request(path + "/reservations", "POST", {"customer":"Smoke demo", "quantity":2}, 201)
    request(path + "/reservations", "POST", {"customer":"Overflow", "quantity":1}, 409)
    assert request(path)['quantity_available'] == 0
    request(front + f"/api/reservations/{reservation['id']}/cancel", "POST")
    assert request(path)['quantity_available'] == 2
    checks.append("Reservation decrements stock, overselling blocked, cancellation restores stock")
    before = request(front + "/api/stats")
    reservation = request(path + "/reservations", "POST", {"customer":"Smoke demo", "quantity":1}, 201)
    pickup_path = front + f"/api/reservations/{reservation['id']}/pickup"
    request(pickup_path, "POST", {"pickup_code":"WRONG"}, 422)
    request(pickup_path, "POST", {"pickup_code":reservation['pickup_code']})
    request(pickup_path, "POST", {"pickup_code":reservation['pickup_code']}, 409)
    after = request(front + "/api/stats")
    assert after['meals_rescued'] == before['meals_rescued'] + 1
    assert after['savings_paise'] == before['savings_paise'] + 20000
    checks.append("Pickup code validated, duplicate pickup blocked, persisted impact totals")
    # Keep reservation history, but close the synthetic listing to new reservations.
    request(path, "PUT", {**payload, "status":"PAUSED"})
    request(path, "DELETE", expected=409)
    checks.append("Reserved listing history protected; synthetic listing paused")
    metrics = request(back + '/metrics')
    assert 'lastbite_http_requests_total' in metrics
    assert 'route="/api/listings/{listing_id}"' in metrics
    checks.append("Prometheus metrics with bounded route labels")
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
