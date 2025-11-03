import asyncio
import io
from datetime import datetime, timezone
from typing import Optional

from PIL import Image

from app.core.logging import get_logger
from app.services.rala_pipeline import radar_data_manager


logger = get_logger(__name__)


class RadarService:
    def __init__(self, refresh_seconds: int = 180) -> None:
        self.refresh_seconds = refresh_seconds
        self._latest_timestamp: Optional[str] = None
        # In a full implementation, we would cache pre-rendered tiles per z/x/y.
        # For now we fall back to a generated placeholder tile while wiring MRMS.

    async def start_background_refresh(self) -> None:
        # Placeholder: no-op loop until MRMS integration is completed.
        while True:
            try:
                await radar_data_manager.refresh_from_mrms()
                self._latest_timestamp = radar_data_manager.latest_timestamp()
            except Exception as exc:  # pragma: no cover
                logger.warning("Radar refresh failed: %s", exc)
            await asyncio.sleep(self.refresh_seconds)

    def get_latest_timestamp(self) -> str:
        return self._latest_timestamp or radar_data_manager.latest_timestamp()

    def get_tile_png(self, z: int, x: int, y: int) -> bytes:
        # Attempt real rendering; fallback to placeholder internally
        return radar_data_manager.render_tile(z, x, y)


radar_service = RadarService()

