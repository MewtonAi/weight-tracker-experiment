from fastapi import APIRouter
from fastapi.responses import Response

from app.models.schemas import GoalUpdate, WeightEntryCreate, WeightEntryUpdate
from app.services.weight_service import WeightService

router = APIRouter()
service = WeightService()


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.get("/entries")
def list_entries() -> list[dict]:
    return service.list_entries()


@router.get("/entries/export.csv")
def export_entries_csv() -> Response:
    csv_content = service.export_entries_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="weight-entries.csv"'},
    )


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


@router.get("/goal")
def get_goal() -> dict:
    return service.get_goal().model_dump()


@router.put("/goal")
def update_goal(payload: GoalUpdate) -> dict:
    return service.update_goal(payload).model_dump()
