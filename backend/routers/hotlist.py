"""API router for hotlist endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/hotlist", tags=["热点"])


class HotItemResponse(BaseModel):
    id: str
    date: str
    rank: int
    title: str
    source: str
    source_url: Optional[str] = None
    publish_time: Optional[str] = None
    summary: str
    keywords: list[str]
    heat_score: int
    background: Optional[str] = None
    related_figures: Optional[str] = None
    latest_progress: Optional[str] = None
    potential_impact: Optional[str] = None


class HotListResponse(BaseModel):
    date: str
    total: int
    items: list[HotItemResponse]


def get_store(request: Request):
    return request.app.state.store


@router.get("", response_model=HotListResponse)
async def get_hotlist(date: Optional[str] = None, request: Request = None):
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    store = get_store(request)
    items = store.load_hotlist(date)

    if not items:
        raise HTTPException(
            status_code=404,
            detail=f"No hotlist found for date {date}. Run the generate command first.",
        )

    return HotListResponse(
        date=date,
        total=len(items),
        items=[HotItemResponse(**item.model_dump()) for item in items],
    )


@router.get("/{item_id}")
async def get_hotitem(item_id: str, request: Request = None):
    parts = item_id.rsplit("_", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    date, _ = parts
    store = get_store(request)
    items = store.load_hotlist(date)

    for item in items:
        if item.id == item_id:
            return item.model_dump()

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@router.get("/dates/list")
async def list_available_dates(request: Request = None):
    store = get_store(request)
    dates = store.list_dates()
    return {"dates": dates, "total": len(dates)}


@router.post("/generate")
async def generate_daily(body: dict = None, request: Request = None):
    """Run the full pipeline: scrape → summarize → script → TTS."""
    from backend.pipeline import run_daily_pipeline

    style = "default"
    custom_prompt = ""
    date = None
    if body:
        style = str(body.get("style", "default"))
        custom_prompt = str(body.get("custom_prompt", ""))
        date = body.get("date")

    store = get_store(request)
    result = await run_daily_pipeline(store, date=date, style=style, custom_prompt=custom_prompt)
    return {"status": "ok", **result}
