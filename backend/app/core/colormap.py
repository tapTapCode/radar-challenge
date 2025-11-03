from typing import Tuple


# Simple dBZ color scale (light to heavy)
COLOR_STOPS = [
    (-10, (100, 100, 255)),  # light blue
    (0, (0, 204, 255)),
    (10, (0, 255, 204)),
    (20, (0, 255, 0)),
    (30, (170, 255, 0)),
    (35, (255, 238, 0)),
    (40, (255, 204, 0)),
    (45, (255, 153, 0)),
    (50, (255, 102, 0)),
    (55, (255, 0, 0)),
    (60, (204, 0, 0)),
    (65, (153, 0, 0)),
]


def color_for_dbz(dbz: float, alpha: int = 180) -> Tuple[int, int, int, int]:
    last_color = (0, 0, 0)
    for threshold, color in COLOR_STOPS:
        last_color = color
        if dbz < threshold:
            return (*last_color, alpha)
    return (*last_color, alpha)

