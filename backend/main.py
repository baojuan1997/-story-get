"""FastAPI backend entry point."""
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.storage import DataStore
from backend.routers import hotlist, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("[App] Starting up...")

    project_root = Path(__file__).parent.parent
    audio_dir = project_root / "data" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    print("[App] Ready.")

    yield

    print("[App] Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    audio_dir = data_dir / "audio"

    app = FastAPI(
        title='"误"联网原住民 — 播客助手',
        description="每日热点抓取与播客内容自动生成系统",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.data_dir = data_dir
    app.state.audio_dir = audio_dir
    app.state.store = DataStore(str(data_dir))

    app.include_router(hotlist.router)
    app.include_router(summary.router)

    @app.get("/api/health")
    async def health():
        return {
            "status": "ok",
            "version": "1.0.0",
            "service": '"误"联网原住民播客助手',
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
