import csv
import io
import sqlite3

from app.models.schemas import GoalOut, GoalUpdate, StatsOut, WeightEntryCreate, WeightEntryUpdate
from app.repositories.weight_repository import WeightRepository
from app.services.errors import EntryDateExistsError, NotFoundError


class WeightService:
    def __init__(self, repository: WeightRepository | None = None) -> None:
        self.repository = repository or WeightRepository()

    def list_entries(self) -> list[dict]:
        return self.repository.list_entries()

    def create_entry(self, payload: WeightEntryCreate) -> dict:
        try:
            return self.repository.create_entry(
                entry_date=payload.entry_date.isoformat(),
                weight_kg=payload.weight_kg,
                note=payload.note,
            )
        except sqlite3.IntegrityError as exc:
            if self.repository.is_unique_violation(exc):
                raise EntryDateExistsError(payload.entry_date.isoformat()) from exc
            raise

    def update_entry(self, entry_id: int, payload: WeightEntryUpdate) -> dict:
        existing = self.repository.get_entry_by_id(entry_id)
        if not existing:
            raise NotFoundError()

        try:
            return self.repository.update_entry(
                entry_id=entry_id,
                entry_date=payload.entry_date.isoformat(),
                weight_kg=payload.weight_kg,
                note=payload.note,
            )
        except sqlite3.IntegrityError as exc:
            if self.repository.is_unique_violation(exc):
                raise EntryDateExistsError(payload.entry_date.isoformat()) from exc
            raise

    def delete_entry(self, entry_id: int) -> dict:
        deleted = self.repository.delete_entry(entry_id)
        if not deleted:
            raise NotFoundError()
        return {"ok": True}

    def stats(self) -> StatsOut:
        data = self.repository.list_entries_asc()
        if not data:
            return StatsOut(
                current_weight=None,
                entries_count=0,
                change_last_7=None,
                avg_last_7=None,
            )

        current_weight = data[-1]["weight_kg"]
        last_7 = data[-7:]
        avg_last_7 = round(sum(x["weight_kg"] for x in last_7) / len(last_7), 2)

        change_last_7 = None
        if len(last_7) >= 2:
            change_last_7 = round(last_7[-1]["weight_kg"] - last_7[0]["weight_kg"], 2)

        return StatsOut(
            current_weight=current_weight,
            entries_count=len(data),
            change_last_7=change_last_7,
            avg_last_7=avg_last_7,
        )

    def get_goal(self) -> GoalOut:
        goal_weight = self.repository.get_goal_weight()
        current_weight = self.stats().current_weight

        if goal_weight is None or current_weight is None:
            return GoalOut(
                goal_weight_kg=goal_weight,
                current_weight=current_weight,
                remaining_kg=None,
                progress_percent=None,
            )

        remaining_kg = round(current_weight - goal_weight, 2)
        if current_weight <= goal_weight:
            progress_percent = 100.0
        else:
            progress_percent = round(max(0.0, min(100.0, (goal_weight / current_weight) * 100)), 1)

        return GoalOut(
            goal_weight_kg=goal_weight,
            current_weight=current_weight,
            remaining_kg=remaining_kg,
            progress_percent=progress_percent,
        )

    def update_goal(self, payload: GoalUpdate) -> GoalOut:
        self.repository.upsert_goal_weight(payload.goal_weight_kg)
        return self.get_goal()

    def export_entries_csv(self) -> str:
        rows = self.repository.list_entries_for_export()
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["date", "weight_kg", "note"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "date": row["entry_date"],
                    "weight_kg": row["weight_kg"],
                    "note": row["note"] or "",
                }
            )
        return output.getvalue()
