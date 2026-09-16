"""Pydantic v2 request/response models for the ExpenseFlow API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    """Payload to submit a new expense."""

    description: str
    amount_minor: int = Field(gt=0, description="Amount in integer minor units, must be positive")
    currency: str = Field(min_length=3, max_length=3, description="3-letter currency code")
    category: str
    submitted_by: str


class ExpenseOut(BaseModel):
    """An expense as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    submitted_by: str
    category: str
    amount_minor: int
    currency: str
    amount_base_minor: int
    status: str
    created_at: datetime


class InsightOut(BaseModel):
    """An AI-generated spending insight."""

    summary: str
    bullets: list[str]


class HealthOut(BaseModel):
    """Health check response."""

    status: str
    count: int
