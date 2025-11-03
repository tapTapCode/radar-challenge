from typing import Optional, Tuple
from datetime import datetime, timezone
import io

from PIL import Image

from app.core.colormap import color_for_dbz
from app.core.tiling import tile_bounds_lonlat
from app.core.logging import get_logger
from app.clients.mrms import MRMSClient


logger = get_logger(__name__)


try:
    import numpy as np  # type: ignore
    import xarray as xr  # type: ignore
    _HAVE_NUMPY = True
except Exception:  # pragma: no cover
    np = None  # type: ignore
    xr = None  # type: ignore
    _HAVE_NUMPY = False


class RadarDataManager:
    def __init__(self) -> None:
        self._latest_timestamp_iso: Optional[str] = None
        self._ds: Optional["xr.Dataset"] = None
        self._var_name = "RALA"  # expected RALA variable; may vary by file
        self._client = MRMSClient()

    async def refresh_from_mrms(self) -> None:
        """Download and parse the latest RALA into memory (best effort)."""
        try:
            ts = await self._client.get_latest_rala_timestamp()
            if not ts:
                logger.info("No latest RALA timestamp discovered yet")
                return
            # TODO: fetch GRIB2 content for ts once implemented in client
            # For now, we only record the timestamp to show freshness
            self._latest_timestamp_iso = ts
            # Parsing not yet implemented without system libs; keep ds=None
        except Exception as exc:  # pragma: no cover
            logger.warning("RALA refresh failed: %s", exc)

    def latest_timestamp(self) -> str:
        return self._latest_timestamp_iso or datetime.now(timezone.utc).isoformat()

    def render_tile(self, z: int, x: int, y: int) -> bytes:
        if not _HAVE_NUMPY or self._ds is None:
            return self._render_placeholder_tile()

        # Placeholder path until actual resampling implemented
        return self._render_placeholder_tile()

    def _render_placeholder_tile(self) -> bytes:
        size = 256
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        # Draw a subtle gradient indicating "data area"
        for j in range(size):
            dbz = -10 + 75 * (j / size)
            rgba = color_for_dbz(dbz, alpha=120)
            for i in range(size):
                if (i + j) % 3 == 0:
                    img.putpixel((i, j), rgba)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


radar_data_manager = RadarDataManager()

