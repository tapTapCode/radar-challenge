from typing import Optional
from datetime import datetime, timezone
import io

from PIL import Image

from app.core.colormap import color_for_dbz
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
            self._latest_timestamp_iso = ts
            # Attempt to download and parse GRIB2 if libs available
            if _HAVE_NUMPY and xr is not None:
                try:
                    content = await self._client.fetch_rala_grib_for_time(ts)
                    # cfgrib requires ecCodes installed on system
                    self._ds = xr.open_dataset(io.BytesIO(content), engine="cfgrib", backend_kwargs={
                        "indexpath": "",
                    })
                except Exception as exc:
                    logger.info("GRIB2 parse not available yet: %s", exc)
                    self._ds = None
        except Exception as exc:  # pragma: no cover
            logger.warning("RALA refresh failed: %s", exc)

    def latest_timestamp(self) -> str:
        return self._latest_timestamp_iso or datetime.now(timezone.utc).isoformat()

    def render_tile(self, z: int, x: int, y: int) -> bytes:
        if not _HAVE_NUMPY or self._ds is None:
            return self._render_placeholder_tile()

        # Try to render a very naive image by slicing the data grid into a tile-sized image.
        # This is a placeholder for true projection-aware resampling but uses real data values.
        try:
            var_candidates = [self._var_name, "unknown"]
            for name in self._ds.data_vars:
                if name.upper().startswith("RAL"):
                    var_candidates.insert(0, name)
            arr = None
            for n in var_candidates:
                if n in self._ds:
                    arr = self._ds[n]
                    break
            if arr is None:
                return self._render_placeholder_tile()

            data = np.array(arr.values)
            # Collapse extra dims if present, keep a 2D field
            while data.ndim > 2:
                data = data[0]
            h, w = data.shape
            # Scale to 256x256 for a quick preview; no projection handling
            img = Image.new("RGBA", (256, 256))
            yy = (np.linspace(0, h - 1, 256)).astype(int)
            xx = (np.linspace(0, w - 1, 256)).astype(int)
            for j, yv in enumerate(yy):
                row = data[yv, xx]
                for i, v in enumerate(row):
                    try:
                        rgba = color_for_dbz(float(v))
                    except Exception:
                        rgba = (0, 0, 0, 0)
                    img.putpixel((i, j), rgba)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as exc:
            logger.info("Tile render fallback due to error: %s", exc)
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

