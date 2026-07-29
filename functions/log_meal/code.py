#input_type_name: LogMealInput
#output_type_name: LogMealResult
#function_name: log_meal

from datetime import datetime, timezone
from typing import Any, Literal
from zoneinfo import ZoneInfo

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel, Field


class LogMealInput(BaseModel):
    name: str
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"] = "snack"
    logged_at: str | None = None
    calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    quantity: float | None = None
    unit: str | None = None
    source: Literal["manual", "telegram"] = "manual"
    notes: str | None = None
    raw_input: dict[str, Any] = Field(default_factory=dict)
    image_path: str | None = None
    dedupe_key: str | None = None
    timezone_name: str = "Asia/Kolkata"


class LogMealResult(BaseModel):
    meal_id: str
    log_date: str
    meal_count: int
    calories: float
    protein_g: float
    trigger_id: str | None = None
    duplicate: bool = False


def _items(result: Any) -> list[dict[str, Any]]:
    raw = result.to_dict() if hasattr(result, "to_dict") else result
    return list((raw or {}).get("items") or [])


async def log_meal(ctx: FunctionContext, data: LogMealInput) -> LogMealResult:
    name = data.name.strip()
    if not name:
        raise ValueError("name is required")
    pod = Pod.from_env()
    logged = (
        datetime.fromisoformat(data.logged_at.replace("Z", "+00:00"))
        if data.logged_at
        else datetime.now(timezone.utc)
    )
    if logged.tzinfo is None:
        logged = logged.replace(tzinfo=timezone.utc)
    logged_at = logged.astimezone(timezone.utc).isoformat()
    try:
        local_timezone = ZoneInfo(data.timezone_name)
    except Exception as exc:
        raise ValueError(f"unknown timezone_name: {data.timezone_name}") from exc
    log_date = logged.astimezone(local_timezone).date().isoformat()

    if data.dedupe_key:
        existing = _items(
            pod.records.list(
                "meals",
                limit=1,
                filter=[{"field": "dedupe_key", "op": "eq", "value": data.dedupe_key}],
            )
        )
        if existing:
            meal = existing[0]
            days = _items(
                pod.records.list(
                    "daily_nutrition",
                    limit=1,
                    filter=[{"field": "log_date", "op": "eq", "value": log_date}],
                )
            )
            day = days[0] if days else {}
            return LogMealResult(
                meal_id=str(meal["id"]),
                log_date=log_date,
                meal_count=int(day.get("meal_count") or 0),
                calories=float(day.get("calories") or 0),
                protein_g=float(day.get("protein_g") or 0),
                duplicate=True,
            )
    else:
        recent = _items(
            pod.records.list(
                "meals",
                limit=10,
                filter=[
                    {"field": "name", "op": "eq", "value": name},
                    {"field": "source", "op": "eq", "value": data.source},
                ],
            )
        )
        for candidate in recent:
            candidate_time = datetime.fromisoformat(
                str(candidate["logged_at"]).replace("Z", "+00:00")
            )
            same_estimate = (
                abs(float(candidate.get("calories") or 0) - float(data.calories or 0)) < 0.1
                and abs(float(candidate.get("protein_g") or 0) - float(data.protein_g or 0)) < 0.1
                and abs(float(candidate.get("carbs_g") or 0) - float(data.carbs_g or 0)) < 0.1
                and abs(float(candidate.get("fat_g") or 0) - float(data.fat_g or 0)) < 0.1
            )
            if same_estimate and abs((logged - candidate_time).total_seconds()) <= 180:
                days = _items(
                    pod.records.list(
                        "daily_nutrition",
                        limit=1,
                        filter=[{"field": "log_date", "op": "eq", "value": log_date}],
                    )
                )
                day = days[0] if days else {}
                return LogMealResult(
                    meal_id=str(candidate["id"]),
                    log_date=log_date,
                    meal_count=int(day.get("meal_count") or 0),
                    calories=float(day.get("calories") or 0),
                    protein_g=float(day.get("protein_g") or 0),
                    duplicate=True,
                )

    values = {
        "name": name,
        "meal_type": data.meal_type,
        "logged_at": logged_at,
        "calories": round(float(data.calories or 0), 1),
        "protein_g": round(float(data.protein_g or 0), 1),
        "carbs_g": round(float(data.carbs_g or 0), 1),
        "fat_g": round(float(data.fat_g or 0), 1),
        "quantity": data.quantity,
        "unit": data.unit,
        "source": data.source,
        "notes": data.notes,
        "raw_input": data.raw_input,
        "image_path": data.image_path,
        "dedupe_key": data.dedupe_key,
        "review_status": "pending",
        "needs_attention": False,
    }
    meal = pod.table("meals").create(values)

    days = _items(
        pod.records.list(
            "daily_nutrition",
            limit=1,
            filter=[{"field": "log_date", "op": "eq", "value": log_date}],
        )
    )
    if days:
        day = days[0]
        count = int(day.get("meal_count") or 0) + 1
        calories = round(float(day.get("calories") or 0) + values["calories"], 1)
        protein = round(float(day.get("protein_g") or 0) + values["protein_g"], 1)
        carbs = round(float(day.get("carbs_g") or 0) + values["carbs_g"], 1)
        fat = round(float(day.get("fat_g") or 0) + values["fat_g"], 1)
        calorie_target = float(day.get("calorie_target") or 2000)
        protein_target = float(day.get("protein_target_g") or 100)
        pod.table("daily_nutrition").update(
            day["id"],
            {
                "meal_count": count,
                "calories": calories,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "calorie_progress_percent": round(calories / calorie_target * 100, 1),
                "protein_progress_percent": round(protein / protein_target * 100, 1),
                "summary": f"{count} meals · {calories:.0f} kcal · {protein:.0f} g protein",
            },
        )
    else:
        count = 1
        calories = values["calories"]
        protein = values["protein_g"]
        carbs = values["carbs_g"]
        fat = values["fat_g"]
        pod.table("daily_nutrition").create(
            {
                "log_date": log_date,
                "meal_count": count,
                "reviewed_count": 0,
                "calories": calories,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "calorie_target": 2000,
                "protein_target_g": 100,
                "calorie_progress_percent": round(calories / 2000 * 100, 1),
                "protein_progress_percent": round(protein / 100 * 100, 1),
                "attention_count": 0,
                "summary": f"1 meal · {calories:.0f} kcal · {protein:.0f} g protein",
            }
        )

    trigger = pod.table("meal_triggers").create(
        {
            "meal_id": str(meal["id"]),
            "trigger_type": "meal_logged",
            "status": "queued",
            "source_event": {
                "name": name,
                "meal_type": data.meal_type,
                "calories": values["calories"],
                "protein_g": values["protein_g"],
                "source": data.source,
            },
        }
    )
    return LogMealResult(
        meal_id=str(meal["id"]),
        log_date=log_date,
        meal_count=count,
        calories=calories,
        protein_g=protein,
        trigger_id=str(trigger["id"]),
    )
