import os
import tempfile
from pathlib import Path

# Never point these tests at the application's DATABASE_URL. CI may provide only
# a dedicated disposable TEST_DATABASE_URL; otherwise use a fresh SQLite file.
_test_dir = tempfile.TemporaryDirectory(prefix="relaydesk-tests-")
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{Path(_test_dir.name) / 'tests.db'}")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import delete
from app.db import engine, SessionLocal
from app.main import app
from app.models import Ticket, TicketEvent


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")
    engine.dispose()
    _test_dir.cleanup()


@pytest.fixture(autouse=True)
def empty_database(migrated_database):
    with SessionLocal() as db:
        db.execute(delete(TicketEvent))
        db.execute(delete(Ticket))
        db.commit()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def payload():
    return {"title": "VPN access for new engineer", "requester": "Alex Morgan",
            "category": "ACCESS", "priority": "HIGH", "assignee": "Sam Lee", "status": "OPEN"}
