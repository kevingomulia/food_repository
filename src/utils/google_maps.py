import re
import requests
from urllib.parse import unquote, urlparse
from sqlalchemy import text
from utils.db import get_engine

def resolve_gmaps_shortlink(url):
    """Follows a short Google Maps link and returns the resolved long URL."""
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        return response.url
    except Exception:
        return None

def extract_coordinates_from_url(url):
    """Extracts lat/lon from a resolved Google Maps URL."""
    if not url:
        return None, None
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def get_nearest_mrt_stations(lat, lon, limit=2, max_distance_km=1.0):
    """Finds the nearest MRT stations within a max distance using the Haversine formula."""
    query = """
        SELECT
            name,
            (
                6371 * acos(
                    cos(radians(:lat)) * cos(radians(latitude)) *
                    cos(radians(longitude) - radians(:lon)) +
                    sin(radians(:lat)) * sin(radians(latitude))
                )
            ) AS distance
        FROM mrt_stations
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (
            6371 * acos(
                cos(radians(:lat)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(:lon)) +
                sin(radians(:lat)) * sin(radians(latitude))
            )
        ) <= :max_distance_km
        ORDER BY distance
        LIMIT :limit;
    """
    try:
        with get_engine().connect() as conn:
            result = conn.execute(
                text(query),
                {"lat": lat, "lon": lon, "limit": limit, "max_distance_km": max_distance_km}
            )
            return [row.name for row in result]
    except Exception as e:
        print("Error:", e)
        return []


def extract_place_name_from_gmaps(url: str) -> str:
    try:
        path = urlparse(url).path
        if "/place/" in path:
            name_segment = path.split("/place/")[1].split("/")[0]
            return unquote(name_segment.replace("+", " ")).strip()
    except Exception as e:
        print(f"Error extracting place name from URL: {e}")
    return ""