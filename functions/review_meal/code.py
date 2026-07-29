#input_type_name: ReviewMealInput
#output_type_name: ReviewMealResult
#function_name: review_meal

from datetime import datetime, timezone
from typing import Any, Literal
from zoneinfo import ZoneInfo

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel, Field


class ReviewMealInput(BaseModel):
    meal_id: str
    trigger_id: str | None = None
    meal_score: int
    protein_signal: Literal["low", "steady", "high"]
    plant_signal: Literal["none", "some", "strong"]
    needs_attention: bool = False
    review_note: str
    next_move: str
    signal_type: Literal["protein_gap", "low_confidence", "large_estimate", "pattern", "info"] | None = None
    signal_title: str | None = None
    signal_body: str | None = None
    signal_severity: Literal["info", "low", "medium", "high"] = "info"
    signal_metadata: dict[str, Any] = Field(default_factory=dict)


class ReviewMealResult(BaseModel):
    meal_id: str
    review_status: str
    meal_score: int
    signal_id: str | None = None
    duplicate: bool = False


def _items(result: Any) -> list[dict[str, Any]]:
    raw = result.to_dict() if hasattr(result, "to_dict") else result
    return list((raw or {}).get("items") or [])


def _one(pod: Pod, table: str, record_id: str) -> dict[str, Any]:
    rows = _items(
        pod.records.list(
            table,
            limit=1,
            filter=[{"field": "id", "op": "eq", "value": record_id}],
        )
    )
    if not rows:
        raise ValueError(f"{table} record not found: {record_id}")
    return rows[0]


async def review_meal(ctx: FunctionContext, data: ReviewMealInput) -> ReviewMealResult:
    if data.meal_score < 1 or data.meal_score > 5:
        raise ValueError("meal_score must be between 1 and 5")
    pod = Pod.from_env()
    meal = _one(pod, "meals", data.meal_id)
    if meal.get("review_status") == "reviewed":
        if data.trigger_id:
            pod.table("meal_triggers").update(data.trigger_id, {"status": "processed"})
        return ReviewMealResult(
            meal_id=data.meal_id,
            review_status="reviewed",
            meal_score=int(meal.get("meal_score") or data.meal_score),
            duplicate=True,
        )

    pod.table("meals").update(
        data.meal_id,
        {
            "review_status": "reviewed",
            "meal_score": data.meal_score,
            "protein_signal": data.protein_signal,
            "plant_signal": data.plant_signal,
            "needs_attention": data.needs_attention,
            "review_note": data.review_note.strip(),
            "next_move": data.next_move.strip(),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    logged = datetime.fromisoformat(str(meal["logged_at"]).replace("Z", "+00:00"))
    log_date = logged.astimezone(ZoneInfo("Asia/Kolkata")).date().isoformat()
    days = _items(
        pod.records.list(
            "daily_nutrition",
            limit=1,
            filter=[{"field": "log_date", "op": "eq", "value": log_date}],
        )
    )
    if days:
        day = days[0]
        pod.table("daily_nutrition").update(
            day["id"],
            {
                "reviewed_count": int(day.get("reviewed_count") or 0) + 1,
                "attention_count": int(day.get("attention_count") or 0)
                + (1 if data.needs_attention else 0),
            },
        )

    signal_id = None
    if data.signal_type and data.signal_title and data.signal_body:
        signal_key = f"review:{data.signal_type}:{data.meal_id}"
        existing = _items(
            pod.records.list(
                "meal_signals",
                limit=1,
                filter=[{"field": "signal_key", "op": "eq", "value": signal_key}],
            )
        )
        if existing:
            signal_id = str(existing[0]["id"])
        else:
            signal = pod.table("meal_signals").create(
                {
                    "meal_id": data.meal_id,
                    "signal_type": data.signal_type,
                    "severity": data.signal_severity,
                    "title": data.signal_title,
                    "body": data.signal_body,
                    "status": "open",
                    "signal_key": signal_key,
                    "metadata": data.signal_metadata,
                }
            )
            signal_id = str(signal["id"])
    if data.trigger_id:
        pod.table("meal_triggers").update(data.trigger_id, {"status": "processed"})
    return ReviewMealResult(
        meal_id=data.meal_id,
        review_status="reviewed",
        meal_score=data.meal_score,
        signal_id=signal_id,
    )
