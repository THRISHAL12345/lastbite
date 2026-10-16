from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["OPEN", "IN_PROGRESS", "RESOLVED"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "URGENT"]
Category = Literal["ACCESS", "HARDWARE", "SOFTWARE", "NETWORK", "OTHER"]


class TicketWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    requester: str = Field(min_length=1, max_length=120)
    assignee: str = Field(default="Unassigned", min_length=1, max_length=120)
    category: Category = "OTHER"
    priority: Priority = "MEDIUM"
    status: Status = "OPEN"


class TicketOut(TicketWrite):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    due_at: datetime
    resolved_at: datetime | None
    overdue: bool


class CommentWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(min_length=1, max_length=2000)


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    kind: str
    message: str
    created_at: datetime


class TicketPage(BaseModel):
    items: list[TicketOut]
    total: int
    limit: int
    offset: int
