# Radar Coding Challenge

Full-stack weather radar display using MRMS Reflectivity at Lowest Altitude (RALA).

## Stack
- Frontend: React + Vite + TypeScript + Leaflet (map library)
- Backend: Python FastAPI (fetch/process MRMS RALA, serve tiles + API)
- Hosting: Render.com (backend), Netlify/Vercel (frontend) — or both on Render

## Quick Start

### Backend
```bash
# create and activate venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (frontend) and it will request tiles from http://localhost:8000.

## Notes
- No third-party radar tiles are used; data comes directly from MRMS.
- A basemap is used for geographic context. If third-party basemap tiles are not permitted, we can switch to a vector basemap hosted within this project.

## TODO
- Implement MRMS RALA fetch + parse
- Tile service rendering
- Styling polish
- Deployment to Render.com
