from typing import Tuple
import math


WEB_MERCATOR_EPSG = 3857
WGS84_EPSG = 4326


def tile_bounds_lonlat(z: int, x: int, y: int) -> Tuple[float, float, float, float]:
    """Return (min_lon, min_lat, max_lon, max_lat) for a web mercator tile.

    Pure math version; avoids dependency on pyproj for basic tiling needs.
    """
    n = 2 ** z
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_min = _tile_y_to_lat(y + 1, n)
    lat_max = _tile_y_to_lat(y, n)
    return (lon_min, lat_min, lon_max, lat_max)


def _tile_y_to_lat(y: int, n: int) -> float:
    # Inverse of the mercator tile formula
    t = math.pi - (2.0 * math.pi * y) / n
    lat = math.degrees(math.atan(math.sinh(t)))
    return lat

