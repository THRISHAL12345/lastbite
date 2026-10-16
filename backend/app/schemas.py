from datetime import datetime
from typing import Literal
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Category = Literal["BAKERY", "MEALS", "PRODUCE", "DESSERTS"]
Dietary = Literal["VEGETARIAN", "VEGAN", "MIXED"]


class ListingWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=160)
    restaurant: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=3000)
    category: Category = "MEALS"
    dietary: Dietary = "VEGETARIAN"
    allergens: str = Field(default="Ask the kitchen", min_length=1, max_length=300)
    address: str = Field(min_length=1, max_length=240)
    price_paise: int = Field(gt=0, le=1000000, strict=True)
    original_price_paise: int = Field(gt=0, le=1000000, strict=True)
    quantity_total: int = Field(gt=0, le=1000, strict=True)
    pickup_start: AwareDatetime
    pickup_end: AwareDatetime
    status: Literal["ACTIVE", "PAUSED"] = "ACTIVE"

    @model_validator(mode="after")
    def valid_window_and_price(self):
        if self.pickup_end <= self.pickup_start:
            raise ValueError("Pickup end must be after pickup start")
        if self.price_paise > self.original_price_paise:
            raise ValueError("Rescue price cannot exceed original value")
        return self


class ListingOut(ListingWrite):
    id: int
    quantity_available: int
    created_at: datetime
    state: Literal["AVAILABLE", "SOLD_OUT", "EXPIRED", "PAUSED"]
    discount_percent: int


class ListingPage(BaseModel):
    items: list[ListingOut]
    total: int
    limit: int
    offset: int


class ReservationWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    customer: str = Field(min_length=1, max_length=120)
    quantity: int = Field(ge=1, le=20, strict=True)


class PickupWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    pickup_code: str = Field(min_length=1, max_length=12)


class ReservationOut(BaseModel):
    id: int
    listing_id: int
    customer: str
    quantity: int
    unit_price_paise: int
    total_paise: int
    pickup_code: str
    status: Literal["RESERVED", "PICKED_UP", "CANCELLED", "EXPIRED"]
    created_at: datetime
    picked_up_at: datetime | None
    listing_title: str
    restaurant: str
    address: str
    pickup_start: datetime
    pickup_end: datetime
    category: Category
