from datetime import timedelta, timezone
from time import perf_counter
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from .db import get_db
from .models import Ticket, TicketEvent, utcnow
from .schemas import CommentWrite, EventOut, Priority, Status, TicketOut, TicketPage, TicketWrite

app = FastAPI(title="RelayDesk API", version="1.0.0")
REQUESTS = Counter("relaydesk_http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("relaydesk_http_request_duration_seconds", "Request latency", ["method", "route"])
SLA_HOURS = {"URGENT": 4, "HIGH": 8, "MEDIUM": 24, "LOW": 72}


@app.middleware("http")
async def measure_requests(request, call_next):
    start = perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        # Route templates prevent a metric series for every ticket ID or unknown URL.
        route = getattr(request.scope.get("route"), "path", "unmatched")
        if route not in {"/metrics", "/health", "/ready"}:
            REQUESTS.labels(request.method, route, str(status)).inc()
            LATENCY.labels(request.method, route).observe(perf_counter() - start)


def serialize(ticket):
    def aware(value):
        return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value
    data = {column.name: getattr(ticket, column.name) for column in Ticket.__table__.columns}
    for key in ("created_at", "updated_at", "due_at", "resolved_at"):
        data[key] = aware(data[key])
    data["overdue"] = ticket.status != "RESOLVED" and data["due_at"] < utcnow()
    return data


def get_ticket_or_404(db, ticket_id):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(404, "Ticket not found")
    return ticket


@app.get("/")
def root():
    return {"service": "RelayDesk API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(Ticket.id).limit(1))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable or migrations not applied") from None
    return {"status": "READY"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})


@app.get("/api/tickets", response_model=TicketPage)
def list_tickets(status: Status | None = None, priority: Priority | None = None,
                 q: str = Query(default="", max_length=200), overdue: bool = False,
                 limit: int = Query(default=20, ge=1, le=100),
                 offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    query = select(Ticket)
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    if q.strip():
        query = query.where(or_(Ticket.title.icontains(q.strip(), autoescape=True),
                               Ticket.requester.icontains(q.strip(), autoescape=True)))
    if overdue:
        query = query.where(Ticket.status != "RESOLVED", Ticket.due_at < utcnow())
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    tickets = db.scalars(query.order_by(Ticket.created_at.desc(), Ticket.id.desc()).offset(offset).limit(limit))
    return {"items": [serialize(t) for t in tickets], "total": total, "limit": limit, "offset": offset}


@app.get("/api/tickets/stats")
def stats(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all())
    overdue = db.scalar(select(func.count()).select_from(Ticket).where(Ticket.status != "RESOLVED", Ticket.due_at < utcnow()))
    return {"total": sum(counts.values()), "open": counts.get("OPEN", 0),
            "in_progress": counts.get("IN_PROGRESS", 0), "resolved": counts.get("RESOLVED", 0), "overdue": overdue}


@app.get("/api/activity", response_model=list[EventOut])
def activity(db: Session = Depends(get_db)):
    return list(db.scalars(select(TicketEvent).order_by(TicketEvent.id.desc()).limit(12)))


@app.post("/api/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketWrite, db: Session = Depends(get_db)):
    now = utcnow()
    ticket = Ticket(**payload.model_dump(), created_at=now, updated_at=now,
                    due_at=now + timedelta(hours=SLA_HOURS[payload.priority]),
                    resolved_at=now if payload.status == "RESOLVED" else None)
    db.add(ticket)
    db.flush()
    db.add(TicketEvent(ticket_id=ticket.id, message=f"Ticket created: {ticket.title}"))
    db.commit()
    db.refresh(ticket)
    return serialize(ticket)


@app.get("/api/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return serialize(get_ticket_or_404(db, ticket_id))


@app.put("/api/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, payload: TicketWrite, db: Session = Depends(get_db)):
    ticket = get_ticket_or_404(db, ticket_id)
    changes = []
    for field, value in payload.model_dump().items():
        if getattr(ticket, field) != value:
            changes.append(f"{field.replace('_', ' ')}: {getattr(ticket, field)} → {value}" if field in {"status", "priority", "assignee"} else f"{field} updated")
    if payload.status != ticket.status:
        ticket.resolved_at = utcnow() if payload.status == "RESOLVED" else None
    # SLA always starts at creation; reprioritizing or reopening cannot reset the clock.
    ticket.due_at = ticket.created_at + timedelta(hours=SLA_HOURS[payload.priority])
    for field, value in payload.model_dump().items():
        setattr(ticket, field, value)
    if changes:
        ticket.updated_at = utcnow()
        db.add(TicketEvent(ticket_id=ticket.id, message="; ".join(changes)))
    db.commit()
    db.refresh(ticket)
    return serialize(ticket)


@app.delete("/api/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db.delete(get_ticket_or_404(db, ticket_id))
    db.commit()
    return Response(status_code=204)


@app.get("/api/tickets/{ticket_id}/events", response_model=list[EventOut])
def events(ticket_id: int, db: Session = Depends(get_db)):
    get_ticket_or_404(db, ticket_id)
    return list(db.scalars(select(TicketEvent).where(TicketEvent.ticket_id == ticket_id).order_by(TicketEvent.id.desc())))


@app.post("/api/tickets/{ticket_id}/comments", response_model=EventOut, status_code=201)
def comment(ticket_id: int, payload: CommentWrite, db: Session = Depends(get_db)):
    ticket = get_ticket_or_404(db, ticket_id)
    event = TicketEvent(ticket_id=ticket_id, kind="COMMENT", message=payload.message)
    ticket.updated_at = utcnow()
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
