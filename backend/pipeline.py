"""Daily pipeline: scrape → summarize → script → TTS."""
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from backend.scraper import SinaNewsScraper, TencentNewsScraper, WeiboHotScraper
from backend.generator import SummaryGenerator, ScriptWriter
from backend.tts import TTSService


async def run_daily_pipeline(store, date: str = None, style: str = "default", custom_prompt: str = "") -> dict:
    """
    Run the full daily pipeline for the given date (defaults to today).
    Returns a status dict.
    """
    target_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[Pipeline] Starting for {target_date}")

    # ── Step 1: Scrape ─────────────────────────────────
    print("[Pipeline] Step 1/4: Scraping news...")
    scrapers = [
        WeiboHotScraper(),
        SinaNewsScraper(),
        TencentNewsScraper(),
    ]

    all_items = []
    for scraper in scrapers:
        try:
            items = await scraper.scrape()
            print(f"  [{scraper.name}] Got {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            print(f"  [{scraper.name}] Error: {e}")
        finally:
            await scraper.close()

    # Deduplicate by title
    seen_titles = set()
    unique_items = []
    for item in all_items:
        title = item.get("title", "").strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_items.append(item)

    # Re-rank
    unique_items = sorted(unique_items, key=lambda x: x.get("rank", 99))[:20]
    for i, item in enumerate(unique_items, 1):
        item["rank"] = i
        item["heat_score"] = max(0, 10000 - i * 500)

    print(f"[Pipeline] Total unique items: {len(unique_items)}")

    # ── Step 2: Save hotlist ───────────────────────────
    print("[Pipeline] Step 2/4: Saving hotlist...")
    hot_items = store.save_hotlist(target_date, unique_items)

    # ── Step 3: Generate summary & script ──────────────
    print("[Pipeline] Step 3/4: Generating summary and script...")
    summarizer = SummaryGenerator()
    summary_md = summarizer.generate(target_date, unique_items)
    store.save_summary(target_date, summary_md)

    script_writer = ScriptWriter(style=style, custom_prompt=custom_prompt)
    script_md = script_writer.generate(target_date, unique_items, summary_md)
    store.save_script(target_date, script_md)

    # ── Step 4: TTS ─────────────────────────────────────
    print("[Pipeline] Step 4/4: Synthesizing audio...")
    audio_path = str(Path(store.audio_dir) / f"{target_date}_podcast.mp3")
    try:
        tts = TTSService()
        tts.synthesize_sync(script_md, audio_path)
        print(f"[Pipeline] Audio saved: {audio_path}")
    except Exception as e:
        print(f"[Pipeline] TTS error: {e}")
        audio_path = None

    print(f"[Pipeline] Completed for {target_date}.")

    return {
        "date": target_date,
        "hot_items": len(hot_items),
        "summary_chars": len(summary_md),
        "script_chars": len(script_md),
        "audio_saved": audio_path is not None,
    }
