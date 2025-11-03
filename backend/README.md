# Backend Overview

This FastAPI backend serves radar tiles rendered directly from MRMS RALA (Reflectivity at Lowest Altitude). It exposes:

- `GET /latest` — latest data timestamp (ISO8601)
- `GET /tiles/{z}/{x}/{y}.png` — XYZ PNG tiles, no third‑party tiles involved

## Module Layout

- `app/main.py`
  - App factory: sets CORS and includes API router
  - Starts background refresh loop
- `app/api/routes.py`
  - HTTP route handlers; thin layer delegating to services
- `app/services/rala_pipeline.py`
  - Parsing/rendering pipeline for MRMS RALA
  - Handles latest timestamp, tile rendering, and safe fallbacks
- `app/services/radar.py`
  - Orchestrates background refresh and serves tiles via the pipeline
- `app/clients/mrms.py`
  - Discovers/downloads MRMS RALA files (best‑effort; robust patterns can be added)
- `app/core/`
  - `config.py`: basic settings
  - `tiling.py`: web‑mercator tile math
  - `colormap.py`: dBZ → RGBA mapping
  - `logging.py`: logger helper

## Development

- Run dev server: `uvicorn app.main:app --reload --port 8000`
- Tests: `pytest -q`

Notes:
- GRIB2 parsing depends on system libraries (ecCodes) when wired; the pipeline is structured to fall back cleanly when unavailable.
- No third‑party map tiles are used; tiles are rendered from MRMS data.

