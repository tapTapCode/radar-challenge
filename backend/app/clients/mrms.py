from typing import Optional, List
import re
import httpx


class MRMSClient:
    def __init__(self, base_url: str = "https://mrms.ncep.noaa.gov"):
        self.base_url = base_url.rstrip('/')

    async def get_latest_rala_timestamp(self) -> Optional[str]:
        # Best-effort HTML index scraping; product path may vary by environment
        # Example candidate directories to probe (kept minimal, extend as needed)
        candidates: List[str] = [
            f"{self.base_url}/data/2D/RALA/",
            f"{self.base_url}/data/2D/ReflectivityAtLowestAltitude/",
        ]
        async with httpx.AsyncClient(timeout=10) as client:
            for url in candidates:
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        # Look for filenames like RALA_YYYYMMDD-HHMM.grib2 or similar
                        m = re.findall(r"RALA[_-](\d{8})[T\-]?(\d{4})", resp.text)
                        if m:
                            # Return ISO-like approximation (UTC)
                            ymd, hm = m[-1]
                            iso_ts = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}T{hm[:2]}:{hm[2:]}:00Z"
                            return iso_ts
                except Exception:
                    continue
        return None

    async def fetch_rala_grib_for_time(self, iso_timestamp: str) -> bytes:
        # Try to find a matching GRIB2 link from the listing as a robust fallback
        candidates: List[str] = [
            f"{self.base_url}/data/2D/RALA/",
            f"{self.base_url}/data/2D/ReflectivityAtLowestAltitude/",
        ]
        async with httpx.AsyncClient(timeout=20) as client:
            for base in candidates:
                try:
                    idx = await client.get(base)
                    if idx.status_code != 200:
                        continue
                    # Grab the last GRIB2-looking href
                    m = re.findall(r'href=\"([^\"]+(?:grib2|grb2)(?:\.gz)?)\"', idx.text, flags=re.IGNORECASE)
                    if not m:
                        continue
                    url = m[-1]
                    if not url.startswith('http'):
                        url = base.rstrip('/') + '/' + url.lstrip('/')
                    resp = await client.get(url)
                    if resp.status_code == 200 and resp.content:
                        return resp.content
                except Exception:
                    continue
        raise RuntimeError("Unable to download RALA GRIB2 from MRMS")

