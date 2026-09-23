from __future__ import annotations

import math


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_distance_to_path(
    lat: float,
    lon: float,
    points: list[tuple[float, float]],
) -> float:
    if not points:
        return float("inf")
    best = min(haversine_meters(lat, lon, p[0], p[1]) for p in points)
    if len(points) < 2:
        return best
    for i in range(len(points) - 1):
        best = min(best, _distance_to_segment(lat, lon, points[i], points[i + 1]))
    return best


def _distance_to_segment(
    lat: float,
    lon: float,
    a: tuple[float, float],
    b: tuple[float, float],
) -> float:
    # Local equirectangular projection is enough at town scale.
    lat_r = math.radians((a[0] + b[0]) / 2)
    scale_x = math.cos(lat_r) * 111_320
    scale_y = 110_540
    px, py = lon * scale_x, lat * scale_y
    ax, ay = a[1] * scale_x, a[0] * scale_y
    bx, by = b[1] * scale_x, b[0] * scale_y
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
