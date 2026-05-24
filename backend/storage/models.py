"""Models for hot news items."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HotItem(BaseModel):
    """A single hot news item."""
    id: str = Field(..., description="Unique ID, format: YYYY-MM-DD_XXX")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    rank: int = Field(..., ge=1, le=100, description="Hot rank position")
    title: str = Field(..., max_length=200)
    source: str = Field(..., max_length=50)
    source_url: Optional[str] = None
    publish_time: Optional[str] = None
    summary: str = Field(..., max_length=200)
    keywords: list[str] = Field(default_factory=list)
    heat_score: int = Field(default=0, ge=0)
    content: Optional[str] = None
    background: Optional[str] = None
    related_figures: Optional[str] = None
    latest_progress: Optional[str] = None
    potential_impact: Optional[str] = None


class DailyData(BaseModel):
    """All data for a single day."""
    date: str
    hotlist: list[HotItem] = Field(default_factory=list)
    summary_md: Optional[str] = None
    script_md: Optional[str] = None
    audio_path: Optional[str] = None
    generated_at: Optional[str] = None
