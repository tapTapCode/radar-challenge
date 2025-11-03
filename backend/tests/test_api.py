from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_latest_returns_timestamp_isoformat():
    response = client.get("/latest")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    # Basic ISO-8601 shape check
    assert "T" in data["timestamp"] and data["timestamp"].endswith("Z") or "+" in data["timestamp"]


def test_tiles_returns_png_bytes():
    # Choose a reasonable tile (z/x/y) within normal web mercator bounds
    response = client.get("/tiles/4/7/6.png")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/png"
    content = response.content
    # PNG signature check
    assert content[:8] == b"\x89PNG\r\n\x1a\n"

