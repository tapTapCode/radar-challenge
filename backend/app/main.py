from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.services.radar import radar_service
import asyncio

app = FastAPI(title="Radar Challenge Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def _start_refresh_task() -> None:
    # Fire-and-forget background refresh loop; it is fallback-safe
    asyncio.create_task(radar_service.start_background_refresh())

