"""Aderin demo places, mapped onto real streets in Yaba, Lagos for the live map."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Place:
    key: str
    name: str
    latitude: float
    longitude: float
    aliases: tuple[str, ...]
    roads: tuple[str, ...]


# Real OSM-covered points around Tejuosho, Herbert Macaulay, Onike, and Sabo.
PLACES: dict[str, Place] = {
    "shop": Place(
        "shop",
        "Shop",
        6.50815,
        3.37595,
        ("shop", "shopfront", "my shop"),
        ("market-road", "river-road"),
    ),
    "home": Place(
        "home",
        "Home",
        6.51740,
        3.38820,
        ("home", "house"),
        ("market-road", "hill-road", "river-road"),
    ),
    "market": Place(
        "market",
        "Market",
        6.50905,
        3.37810,
        ("market", "market road", "aderin market", "tejuosho"),
        ("market-road",),
    ),
    "pharmacy": Place(
        "pharmacy",
        "Pharmacy",
        6.51020,
        3.37920,
        ("pharmacy", "chemist", "near the pharmacy"),
        ("market-road",),
    ),
    "bus_station": Place(
        "bus_station",
        "Bus Station",
        6.51240,
        3.37120,
        ("bus station", "station", "station road"),
        ("station-road",),
    ),
    "community_centre": Place(
        "community_centre",
        "Community Centre",
        6.50720,
        3.38240,
        ("community centre", "community center", "central avenue"),
        ("central-avenue",),
    ),
    "school": Place(
        "school",
        "School",
        6.51580,
        3.38610,
        ("school", "primary school"),
        ("hill-road",),
    ),
    "river_bridge": Place(
        "river_bridge",
        "River Bridge",
        6.50590,
        3.37880,
        ("river", "river road", "bridge"),
        ("river-road",),
    ),
}


ROAD_LABELS = {
    "market-road": "Market Road",
    "station-road": "Station Road",
    "central-avenue": "Central Avenue",
    "river-road": "River Road",
    "hill-road": "Hill Road",
}


def normalize_text(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())


def resolve_place(text: str | None) -> Place | None:
    if not text:
        return None
    needle = normalize_text(text)
    for place in PLACES.values():
        names = {normalize_text(place.name), place.key.replace("_", " "), *place.aliases}
        for alias in names:
            if needle == alias:
                return place
            tokens = alias.split()
            if len(tokens) >= 2 and alias in needle:
                return place
    return None


def road_key_from_name(text: str | None) -> str | None:
    if not text:
        return None
    needle = normalize_text(text)
    for key, label in ROAD_LABELS.items():
        if needle == normalize_text(label) or needle == key.replace("-", " "):
            return key
    place = resolve_place(text)
    if place and len(place.roads) == 1:
        return place.roads[0]
    return None


def places_share_road(a: Place, b: Place) -> bool:
    return bool(set(a.roads) & set(b.roads))
