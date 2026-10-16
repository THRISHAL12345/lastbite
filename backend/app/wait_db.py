"""Wait for connectivity, not application tables, before the migration job."""
import time
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import engine

for attempt in range(60):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        break
    except SQLAlchemyError:
        if attempt == 59:
            raise SystemExit("Database not available after 120 seconds") from None
        time.sleep(2)
