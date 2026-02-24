from datetime import date

from pydantic import BaseModel, Field


class WeightEntryCreate(BaseModel):
    entry_date: date
    weight_kg: float = Field(..., ge=20, le=400)
    note: str | None = Field(default=None, max_length=280)


class WeightEntryUpdate(BaseModel):
    entry_date: date
    weight_kg: float = Field(..., ge=20, le=400)
    note: str | None = Field(default=None, max_length=280)


class WeightEntryOut(BaseModel):
    id: int
    entry_date: str
    weight_kg: float
    note: str | None = None


class StatsOut(BaseModel):
    current_weight: float | None
    entries_count: int
    change_last_7: float | None
    avg_last_7: float | None
