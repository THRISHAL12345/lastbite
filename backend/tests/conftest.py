import os
import tempfile
from pathlib import Path

# This suite never uses the application's DATABASE_URL.
_test_dir = tempfile.TemporaryDirectory(prefix="lastbite-tests-")
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{Path(_test_dir.name) / 'tests.db'}")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import delete
from app.db import engine, SessionLocal
from app.main import app
from app.models import Listing, Reservation, utcnow
from datetime import timedelta


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    backend = Path(__file__).resolve().parents[1]
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "alembic"))
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")
    engine.dispose()
    _test_dir.cleanup()


@pytest.fixture(autouse=True)
def empty_database(migrated_database):
    with SessionLocal() as db:
        db.execute(delete(Reservation))
        db.execute(delete(Listing))
        db.commit()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def payload():
    return {"title": "Sunset supper box", "restaurant": "The Green Table", "description": "Rice, curry and seasonal vegetables.",
            "category": "MEALS", "dietary": "VEGETARIAN", "allergens": "Milk, nuts", "address": "12 Market Lane, Hyderabad",
            "price_paise": 9900, "original_price_paise": 29900, "quantity_total": 5,
            "pickup_start": (utcnow()-timedelta(minutes=10)).isoformat(), "pickup_end": (utcnow()+timedelta(hours=2)).isoformat(), "status":"ACTIVE"}
