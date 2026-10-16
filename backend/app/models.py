from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def utcnow():
    return datetime.now(timezone.utc)


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        CheckConstraint("quantity_total > 0 AND quantity_available >= 0 AND quantity_available <= quantity_total", name="listing_inventory"),
        CheckConstraint("price_paise > 0 AND original_price_paise >= price_paise", name="listing_prices"),
        CheckConstraint("pickup_end > pickup_start", name="listing_pickup_window"),
        CheckConstraint("status IN ('ACTIVE','PAUSED')", name="listing_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    restaurant: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(20))
    dietary: Mapped[str] = mapped_column(String(20))
    allergens: Mapped[str] = mapped_column(String(300), default="Ask the kitchen")
    address: Mapped[str] = mapped_column(String(240))
    price_paise: Mapped[int]
    original_price_paise: Mapped[int]
    quantity_total: Mapped[int]
    quantity_available: Mapped[int]
    pickup_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    pickup_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="reservation_quantity"),
        CheckConstraint("status IN ('RESERVED','PICKED_UP','CANCELLED')", name="reservation_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id", ondelete="RESTRICT"), index=True)
    customer: Mapped[str] = mapped_column(String(120))
    quantity: Mapped[int]
    unit_price_paise: Mapped[int]
    original_unit_price_paise: Mapped[int]
    pickup_code: Mapped[str] = mapped_column(String(12), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="RESERVED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
