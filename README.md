# MRMS RALA Weather Radar (Full‑Stack)

Dynamic weather radar viewer that fetches and renders MRMS Reflectivity at Lowest Altitude (RALA) directly from NOAA. No third‑party map tiles are used. React + Vite + Leaflet frontend; FastAPI backend serving our own XYZ PNG tiles.

## How this meets the challenge
- Process data directly from MRMS (mrms.ncep.noaa.gov) — backend includes an MRMS client and a RALA pipeline scaffold for GRIB2 parsing and tiling.
- No third‑party tiles — the map displays only tiles served by this backend.
- React frontend (Leaflet mapping) — auto‑refreshes to the latest scan.
- Hostable — designed for deployment on Render (backend) and Netlify/Vercel or Render (frontend).
- Styled — MUI cards (header/legend), settings drawer, grid overlay, and tile fade‑in.

## Stack
- Frontend: React + Vite + TypeScript + Leaflet + MUI
- Backend: Python FastAPI

## Local Development
Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Requests to `/api/*` proxy to http://localhost:8000.

## Endpoints
- `GET /latest` → `{ timestamp: ISO8601 }`
- `GET /tiles/{z}/{x}/{y}.png` → PNG tile (Cache‑Control: no‑store)

## Project Structure (short)
- `backend/app/` — FastAPI app
  - `api/` — HTTP routes
  - `clients/mrms.py` — discover/download MRMS assets
  - `services/radar.py` — background refresh + tile serving
  - `services/rala_pipeline.py` — parsing/tiling pipeline (with safe fallbacks)
  - `core/` — config, tiling math, dBZ colormap, logging
- `frontend/` — React app (Leaflet overlay, MUI UI)

## Libraries and justification (concise)
- Leaflet — robust tile handling; building panning/zooming/tiling from scratch is out of scope for a timed challenge.
- FastAPI — quick, typed HTTP and async background tasks.
- Pillow — encode PNG tiles without writing a custom encoder.
- (When fully wired) cfgrib + xarray — standard GRIB2 readers; implementing a GRIB2 parser is not feasible in short time.

## Testing
```bash
cd backend
source .venv/bin/activate
pytest -q
```
Current suite validates `/latest` and `/tiles`.

## Deployment (outline)
- Backend (Render): deploy as a FastAPI/uvicorn service, expose `/latest` and `/tiles`.
- Frontend (Netlify/Vercel/Render): build Vite app; set `/api` proxy to backend URL.

## Notes
- The pipeline is structured to fall back gracefully when GRIB2 system deps are absent; switching to real RALA decoding requires enabling cfgrib/ecCodes.
