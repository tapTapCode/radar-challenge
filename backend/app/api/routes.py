from fastapi import APIRouter, Response
from app.services.radar import radar_service


router = APIRouter()


@router.get("/latest")
async def latest():
    return {"timestamp": radar_service.get_latest_timestamp()}


@router.get("/tiles/{z}/{x}/{y}.png")
async def tiles(z: int, x: int, y: int):
    img_bytes = radar_service.get_tile_png(z=z, x=x, y=y)
    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "no-store, max-age=0, must-revalidate",
            "Pragma": "no-cache",
        },
    )

