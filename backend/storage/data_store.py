"""Data store for hot news items and daily data."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import HotItem, DailyData


class DataStore:
    """File-based data store for all daily data."""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.hotlist_dir = self.data_dir / "hotlist"
        self.summary_dir = self.data_dir / "summary"
        self.script_dir = self.data_dir / "script"
        self.audio_dir = self.data_dir / "audio"
        self._ensure_dirs()

    def _ensure_dirs(self):
        for d in [self.hotlist_dir, self.summary_dir, self.script_dir, self.audio_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _hotlist_path(self, date: str) -> Path:
        return self.hotlist_dir / f"{date}_hotlist.json"

    def _summary_path(self, date: str) -> Path:
        return self.summary_dir / f"{date}_summary.md"

    def _script_path(self, date: str) -> Path:
        return self.script_dir / f"{date}_script.md"

    def _audio_path(self, date: str) -> Path:
        return self.audio_dir / f"{date}_podcast.mp3"

    # ── Hotlist ──────────────────────────────────────────────
    def save_hotlist(self, date: str, items: list[dict]) -> list[HotItem]:
        hot_items = []
        for item in items:
            item["id"] = f"{date}_{str(item['rank']).zfill(3)}"
            item["date"] = date
            hot_items.append(HotItem(**item))

        self._hotlist_path(date).write_text(
            json.dumps([h.model_dump() for h in hot_items], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return hot_items

    def load_hotlist(self, date: str) -> list[HotItem]:
        path = self._hotlist_path(date)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [HotItem(**item) for item in data]

    def hotlist_exists(self, date: str) -> bool:
        return self._hotlist_path(date).exists()

    def list_dates(self) -> list[str]:
        dates = []
        for f in self.hotlist_dir.glob("*_hotlist.json"):
            dates.append(f.stem.replace("_hotlist", ""))
        return sorted(dates, reverse=True)

    # ── Summary ──────────────────────────────────────────────
    def save_summary(self, date: str, content: str):
        self._summary_path(date).write_text(content, encoding="utf-8")

    def load_summary(self, date: str) -> Optional[str]:
        path = self._summary_path(date)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def summary_exists(self, date: str) -> bool:
        return self._summary_path(date).exists()

    # ── Script ───────────────────────────────────────────────
    def save_script(self, date: str, content: str):
        self._script_path(date).write_text(content, encoding="utf-8")

    def load_script(self, date: str) -> Optional[str]:
        path = self._script_path(date)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def script_exists(self, date: str) -> bool:
        return self._script_path(date).exists()

    # ── Audio ────────────────────────────────────────────────
    def save_audio(self, date: str, audio_bytes: bytes):
        path = self._audio_path(date)
        path.write_bytes(audio_bytes)
        return str(path)

    def audio_exists(self, date: str) -> bool:
        return self._audio_path(date).exists()

    def get_audio_path(self, date: str) -> Optional[str]:
        path = self._audio_path(date)
        if path.exists():
            return str(path)
        return None

    # ── Full DailyData ───────────────────────────────────────
    def save_daily_data(self, date: str, hotlist: list[HotItem],
                        summary_md: Optional[str] = None,
                        script_md: Optional[str] = None,
                        audio_path: Optional[str] = None) -> DailyData:
        if summary_md:
            self.save_summary(date, summary_md)
        if script_md:
            self.save_script(date, script_md)

        data = DailyData(
            date=date,
            hotlist=hotlist,
            summary_md=summary_md,
            script_md=script_md,
            audio_path=audio_path,
            generated_at=datetime.now().isoformat(),
        )
        # Also save combined JSON
        combined_path = self.hotlist_dir / f"{date}_daily.json"
        combined_path.write_text(
            json.dumps(data.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return data

    def load_daily_data(self, date: str) -> Optional[DailyData]:
        path = self.hotlist_dir / f"{date}_daily.json"
        if not path.exists():
            return None
        return DailyData(**json.loads(path.read_text(encoding="utf-8")))
