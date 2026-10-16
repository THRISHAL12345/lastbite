from datetime import datetime, timedelta
import pytest
from sqlalchemy.exc import OperationalError
from app.db import SessionLocal, get_db
from app.main import app
from app.models import Ticket, utcnow


def create(client, payload):
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_health_and_readiness(client):
    assert client.get("/health").json() == {"status": "UP"}
    assert client.get("/ready").json() == {"status": "READY"}


def test_readiness_returns_503_on_db_failure(client):
    class FailedDB:
        def execute(self, *_):
            raise OperationalError("unavailable", {}, Exception())
    app.dependency_overrides[get_db] = lambda: FailedDB()
    try:
        assert client.get("/ready").status_code == 503
        assert client.get("/health").status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_create_and_get(client, payload):
    ticket = create(client, payload)
    assert client.get(f"/api/tickets/{ticket['id']}").json() == ticket
    assert ticket["overdue"] is False
    assert datetime.fromisoformat(ticket["due_at"]) - datetime.fromisoformat(ticket["created_at"]) == timedelta(hours=8)


@pytest.mark.parametrize("field,value", [("title", "  "), ("title", "x"*201), ("requester", ""),
                                         ("priority", "INVALID"), ("status", None), ("category", "BAD")])
def test_validation(client, payload, field, value):
    payload[field] = value
    assert client.post("/api/tickets", json=payload).status_code == 422


def test_update_resolve_and_reopen(client, payload):
    ticket = create(client, payload)
    path = f"/api/tickets/{ticket['id']}"
    resolved = client.put(path, json={**payload, "status": "RESOLVED"}).json()
    assert resolved["resolved_at"] is not None
    reopened = client.put(path, json={**payload, "priority": "URGENT"}).json()
    assert reopened["resolved_at"] is None
    assert reopened["due_at"] < ticket["due_at"]
    assert len(client.get(path + "/events").json()) == 3


def test_update_null_rejected(client, payload):
    ticket = create(client, payload)
    assert client.put(f"/api/tickets/{ticket['id']}", json={**payload, "assignee": None}).status_code == 422


def test_filters_and_pagination(client, payload):
    create(client, payload)
    create(client, {**payload, "title": "Laptop replacement", "status": "IN_PROGRESS", "priority": "LOW"})
    assert client.get("/api/tickets?status=OPEN").json()["total"] == 1
    assert client.get("/api/tickets?priority=LOW").json()["items"][0]["title"] == "Laptop replacement"
    assert client.get("/api/tickets?q=vPn").json()["total"] == 1
    assert client.get("/api/tickets?q=%25").json()["total"] == 0
    page = client.get("/api/tickets?limit=1&offset=1").json()
    assert page["total"] == 2 and len(page["items"]) == 1
    assert client.get("/api/tickets?limit=0").status_code == 422


def test_overdue_and_statistics(client, payload):
    ticket = create(client, payload)
    with SessionLocal() as db:
        db.get(Ticket, ticket["id"]).due_at = utcnow() - timedelta(hours=1)
        db.commit()
    create(client, {**payload, "status": "RESOLVED"})
    stats = client.get("/api/tickets/stats").json()
    assert stats == {"total": 2, "open": 1, "in_progress": 0, "resolved": 1, "overdue": 1}
    assert client.get("/api/tickets?overdue=true").json()["items"][0]["overdue"] is True


def test_comments_activity_and_cascade_delete(client, payload):
    ticket = create(client, payload)
    path = f"/api/tickets/{ticket['id']}"
    assert client.post(path + "/comments", json={"message": "Investigating VPN logs"}).status_code == 201
    assert client.post(path + "/comments", json={"message": "  "}).status_code == 422
    assert client.get("/api/activity").json()[0]["kind"] == "COMMENT"
    assert client.delete(path).status_code == 204
    assert client.get(path).status_code == 404
    assert client.get("/api/activity").json() == []


@pytest.mark.parametrize("method,suffix", [("get", ""), ("delete", ""), ("get", "/events"), ("post", "/comments")])
def test_not_found(client, method, suffix):
    kwargs = {"json": {"message": "hello"}} if method == "post" else {}
    assert getattr(client, method)("/api/tickets/99999" + suffix, **kwargs).status_code == 404


def test_metrics_use_route_templates(client, payload):
    ticket = create(client, payload)
    client.get(f"/api/tickets/{ticket['id']}")
    metrics = client.get("/metrics")
    assert "text/plain" in metrics.headers["content-type"]
    assert 'route="/api/tickets/{ticket_id}"' in metrics.text
    assert "relaydesk_http_request_duration_seconds_bucket" in metrics.text
