from fastapi import APIRouter

from app.models.schemas import WeightEntryCreate, WeightEntryUpdate
from app.services.weight_service import WeightService

router = APIRouter()
service = WeightService()


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.get("/entries")
def list_entries() -> list[dict]:
    return service.list_entries()


@router.post("/entries")
def create_entry(payload: WeightEntryCreate) -> dict:
    return service.create_entry(payload)


@router.put("/entries/{entry_id}")
def update_entry(entry_id: int, payload: WeightEntryUpdate) -> dict:
    return service.update_entry(entry_id, payload)


@router.delete("/entries/{entry_id}")
def delete_entry(entry_id: int) -> dict:
    return service.delete_entry(entry_id)


@router.get("/stats")
def stats() -> dict:
    return service.stats().model_dump()
