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

def get_nearest_mrt_stations(lat, lon, limit=2):
    """Finds the nearest MRT stations within a max distance using the Haversine formula."""
    query = """
        SELECT
            name,
            latitude,
            longitude,
            6371 * 2 * ASIN(
                SQRT(
                    POWER(SIN(RADIANS(latitude - :lat) / 2), 2) +
                    COS(RADIANS(:lat)) * COS(RADIANS(latitude)) *
                    POWER(SIN(RADIANS(longitude - :lon) / 2), 2)
                )
            ) AS distance
        FROM "food"."mrt_stations"
        ORDER BY distance ASC
        LIMIT :limit;
    """
    try:
        with get_engine().connect() as conn:
            result = conn.execute(
                text(query),
                {"lat": lat, "lon": lon, "limit": limit}
            )
            return [{"name": row.name, "distance_km": round(row.distance, 2)} for row in result]
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