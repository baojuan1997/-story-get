"""API router for summary and script endpoints."""
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api", tags=["文档"])


class SummaryResponse(BaseModel):
    date: str
    content: str
    exists: bool


class ScriptResponse(BaseModel):
    date: str
    content: str
    exists: bool


class AudioResponse(BaseModel):
    date: str
    path: Optional[str]
    exists: bool


def get_store(request: Request):
    return request.app.state.store


@router.get("/summary/{date}", response_model=SummaryResponse)
async def get_summary(date: str, request: Request = None):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    store = get_store(request)
    content = store.load_summary(date)

    if content is None:
        raise HTTPException(status_code=404, detail=f"No summary found for {date}")

    return SummaryResponse(date=date, content=content, exists=True)


@router.get("/script/{date}", response_model=ScriptResponse)
async def get_script(date: str, request: Request = None):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    store = get_store(request)
    content = store.load_script(date)

    if content is None:
        raise HTTPException(status_code=404, detail=f"No script found for {date}")

    return ScriptResponse(date=date, content=content, exists=True)


@router.get("/audio/{date}")
async def get_audio(date: str, request: Request = None):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    store = get_store(request)
    audio_path = store.get_audio_path(date)

    if audio_path is None or not store.audio_exists(date):
        raise HTTPException(status_code=404, detail=f"No audio found for {date}")

    filename = f"{date}_podcast.mp3"
    audio_file = Path(audio_path)

    def file_iterator(path):
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                yield chunk

    return StreamingResponse(
        file_iterator(str(audio_file)),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(audio_file.stat().st_size),
        },
    )


@router.get("/status/{date}")
async def get_date_status(date: str, request: Request = None):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    store = get_store(request)

    return {
        "date": date,
        "hotlist_exists": store.hotlist_exists(date),
        "summary_exists": store.summary_exists(date),
        "script_exists": store.script_exists(date),
        "audio_exists": store.audio_exists(date),
    }
