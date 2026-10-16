import secrets
from datetime import timezone
from time import perf_counter
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from .db import get_db
from .models import Listing, Reservation, utcnow
from .schemas import Category, Dietary, ListingOut, ListingPage, ListingWrite, PickupWrite, ReservationOut, ReservationWrite

app = FastAPI(title="LastBite API", version="2.0.0")
REQUESTS = Counter("lastbite_http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("lastbite_http_request_duration_seconds", "Request latency", ["method", "route"])


@app.middleware("http")
async def measure_requests(request, call_next):
    start, status = perf_counter(), 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = getattr(request.scope.get("route"), "path", "unmatched")
        if route not in {"/metrics", "/health", "/ready"}:
            REQUESTS.labels(request.method, route, str(status)).inc()
            LATENCY.labels(request.method, route).observe(perf_counter() - start)


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def listing_out(item):
    data = {c.name: getattr(item, c.name) for c in Listing.__table__.columns}
    for key in ("created_at", "pickup_start", "pickup_end"):
        data[key] = aware(data[key])
    data["state"] = ("EXPIRED" if data["pickup_end"] <= utcnow() else "PAUSED" if item.status == "PAUSED"
                     else "SOLD_OUT" if item.quantity_available == 0 else "AVAILABLE")
    data["discount_percent"] = round(100 * (1 - item.price_paise / item.original_price_paise))
    return data


def reservation_out(item, listing):
    data = {c.name: getattr(item, c.name) for c in Reservation.__table__.columns}
    data.update(listing_title=listing.title, restaurant=listing.restaurant, address=listing.address,
                category=listing.category, pickup_start=aware(listing.pickup_start), pickup_end=aware(listing.pickup_end),
                total_paise=item.quantity * item.unit_price_paise)
    for key in ("created_at", "picked_up_at"):
        data[key] = aware(data[key])
    if item.status == "RESERVED" and aware(listing.pickup_end) <= utcnow():
        data["status"] = "EXPIRED"
    return data


def get_listing(db, listing_id, lock=False):
    query = select(Listing).where(Listing.id == listing_id)
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    item = db.scalar(query)
    if item is None:
        raise HTTPException(404, "Meal box not found")
    return item


def reservation_for_change(db, reservation_id):
    item = db.get(Reservation, reservation_id)
    if item is None:
        raise HTTPException(404, "Reservation not found")
    # Lock in the same order as reservation creation to avoid deadlocks.
    listing = get_listing(db, item.listing_id, lock=True)
    db.refresh(item)
    if item.status != "RESERVED":
        raise HTTPException(409, "This reservation has already been completed or cancelled")
    if aware(listing.pickup_end) <= utcnow():
        raise HTTPException(409, "The pickup window has ended")
    return item, listing


@app.get("/")
def root():
    return {"service": "LastBite API", "version": "2.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(Listing.id).limit(1))
        db.execute(select(Reservation.id).limit(1))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable or migrations not applied") from None
    return {"status": "READY"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})


@app.get("/api/listings", response_model=ListingPage)
def listings(category: Category | None = None, dietary: Dietary | None = None,
             state: Literal["AVAILABLE", "SOLD_OUT", "PAUSED", "EXPIRED"] | None = None,
             q: str = Query(default="", max_length=200),
             limit: int = Query(default=12, ge=1, le=100), offset: int = Query(default=0, ge=0),
             db: Session = Depends(get_db)):
    query = select(Listing)
    if category:
        query = query.where(Listing.category == category)
    if dietary:
        query = query.where(Listing.dietary == dietary)
    if q.strip():
        query = query.where(or_(Listing.title.icontains(q.strip(), autoescape=True),
                               Listing.restaurant.icontains(q.strip(), autoescape=True)))
    if state == "EXPIRED":
        query = query.where(Listing.pickup_end <= utcnow())
    elif state:
        query = query.where(Listing.pickup_end > utcnow())
        if state == "PAUSED":
            query = query.where(Listing.status == "PAUSED")
        else:
            query = query.where(Listing.status == "ACTIVE")
            query = query.where(Listing.quantity_available > 0 if state == "AVAILABLE" else Listing.quantity_available == 0)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(query.order_by(Listing.pickup_end, Listing.id).offset(offset).limit(limit))
    return {"items": [listing_out(i) for i in items], "total": total, "limit": limit, "offset": offset}


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    now = utcnow()
    available = db.scalar(select(func.coalesce(func.sum(Listing.quantity_available), 0)).where(Listing.status == "ACTIVE", Listing.pickup_end > now))
    rescued, savings = db.execute(select(func.coalesce(func.sum(Reservation.quantity), 0),
        func.coalesce(func.sum(Reservation.quantity * (Reservation.original_unit_price_paise - Reservation.unit_price_paise)), 0))
        .where(Reservation.status == "PICKED_UP")).one()
    pending = db.scalar(select(func.coalesce(func.sum(Reservation.quantity), 0)).join(Listing)
                        .where(Reservation.status == "RESERVED", Listing.pickup_end > now))
    kitchens = db.scalar(select(func.count(func.distinct(Listing.restaurant))).where(Listing.status == "ACTIVE", Listing.pickup_end > now))
    return {"boxes_available": available, "meals_rescued": rescued, "savings_paise": savings,
            "awaiting_pickup": pending, "active_kitchens": kitchens}


@app.post("/api/listings", response_model=ListingOut, status_code=201)
def create_listing(payload: ListingWrite, db: Session = Depends(get_db)):
    if payload.pickup_end <= utcnow():
        raise HTTPException(422, "Pickup end must be in the future")
    item = Listing(**payload.model_dump(), quantity_available=payload.quantity_total)
    db.add(item)
    db.commit()
    db.refresh(item)
    return listing_out(item)


@app.get("/api/listings/{listing_id}", response_model=ListingOut)
def listing(listing_id: int, db: Session = Depends(get_db)):
    return listing_out(get_listing(db, listing_id))


@app.put("/api/listings/{listing_id}", response_model=ListingOut)
def edit_listing(listing_id: int, payload: ListingWrite, db: Session = Depends(get_db)):
    item = get_listing(db, listing_id, lock=True)
    if aware(item.pickup_end) <= utcnow():
        raise HTTPException(409, "Expired listings cannot be reopened; create a new meal box")
    if payload.pickup_end <= utcnow():
        raise HTTPException(422, "Pickup end must be in the future")
    has_reservations = db.scalar(select(Reservation.id).where(Reservation.listing_id == listing_id).limit(1))
    # A reservation is a promise: do not move its pickup time or change its food details.
    if has_reservations:
        protected = ["title", "restaurant", "description", "category", "dietary", "allergens", "address", "price_paise", "original_price_paise", "pickup_start", "pickup_end"]
        for field in protected:
            current = aware(getattr(item, field)) if field.startswith("pickup_") else getattr(item, field)
            if current != getattr(payload, field):
                raise HTTPException(409, "After a reservation, only stock quantity and availability can change")
    committed = item.quantity_total - item.quantity_available
    if payload.quantity_total < committed:
        raise HTTPException(409, "Stock cannot be lower than boxes already reserved or collected")
    values = payload.model_dump()
    values["quantity_available"] = payload.quantity_total - committed
    result = db.execute(update(Listing).where(Listing.id == listing_id,
        Listing.quantity_total == item.quantity_total, Listing.quantity_available == item.quantity_available).values(**values),
        execution_options={"synchronize_session": False})
    if result.rowcount != 1:
        raise HTTPException(409, "Stock changed; refresh and try again")
    db.commit()
    db.refresh(item)
    return listing_out(item)


@app.delete("/api/listings/{listing_id}", status_code=204)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    item = get_listing(db, listing_id, lock=True)
    if db.scalar(select(Reservation.id).where(Reservation.listing_id == listing_id).limit(1)):
        raise HTTPException(409, "Listings with reservation history cannot be deleted; pause the listing instead")
    db.delete(item)
    db.commit()
    return Response(status_code=204)


@app.post("/api/listings/{listing_id}/reservations", response_model=ReservationOut, status_code=201)
def reserve(listing_id: int, payload: ReservationWrite, db: Session = Depends(get_db)):
    listing = get_listing(db, listing_id, lock=True)
    # Atomic conditional decrement also protects stock when SQLite ignores FOR UPDATE.
    result = db.execute(update(Listing).where(Listing.id == listing_id, Listing.status == "ACTIVE",
        Listing.pickup_end > utcnow(), Listing.quantity_available >= payload.quantity)
        .values(quantity_available=Listing.quantity_available - payload.quantity), execution_options={"synchronize_session": False})
    if result.rowcount != 1:
        raise HTTPException(409, "This box is unavailable or there are not enough boxes left")
    item = Reservation(listing_id=listing_id, customer=payload.customer, quantity=payload.quantity,
                       unit_price_paise=listing.price_paise, original_unit_price_paise=listing.original_price_paise,
                       pickup_code=secrets.token_hex(4).upper())
    db.add(item)
    db.commit()
    db.refresh(item)
    return reservation_out(item, listing)


@app.get("/api/reservations", response_model=list[ReservationOut])
def reservations(limit: int = Query(default=100, ge=1, le=100), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    rows = db.execute(select(Reservation, Listing).join(Listing).order_by(Reservation.id.desc()).offset(offset).limit(limit))
    return [reservation_out(item, listing) for item, listing in rows]


@app.post("/api/reservations/{reservation_id}/cancel", response_model=ReservationOut)
def cancel(reservation_id: int, db: Session = Depends(get_db)):
    item, listing = reservation_for_change(db, reservation_id)
    result = db.execute(update(Reservation).where(Reservation.id == item.id, Reservation.status == "RESERVED")
                        .values(status="CANCELLED"), execution_options={"synchronize_session": False})
    if result.rowcount != 1:
        raise HTTPException(409, "Reservation changed; refresh and try again")
    db.execute(update(Listing).where(Listing.id == listing.id).values(quantity_available=Listing.quantity_available + item.quantity))
    db.commit()
    db.refresh(item)
    return reservation_out(item, listing)


@app.post("/api/reservations/{reservation_id}/pickup", response_model=ReservationOut)
def pickup(reservation_id: int, payload: PickupWrite, db: Session = Depends(get_db)):
    item, listing = reservation_for_change(db, reservation_id)
    if not secrets.compare_digest(payload.pickup_code.upper(), item.pickup_code):
        raise HTTPException(422, "Pickup code does not match")
    if aware(listing.pickup_start) > utcnow():
        raise HTTPException(409, "The pickup window has not started yet")
    result = db.execute(update(Reservation).where(Reservation.id == item.id, Reservation.status == "RESERVED")
                        .values(status="PICKED_UP", picked_up_at=utcnow()), execution_options={"synchronize_session": False})
    if result.rowcount != 1:
        raise HTTPException(409, "Reservation changed; refresh and try again")
    db.commit()
    db.refresh(item)
    return reservation_out(item, listing)
