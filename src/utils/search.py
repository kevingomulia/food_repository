from .db import fetch_dataframe
from sqlalchemy.sql import text

def get_filter_options():
    query_tags = "SELECT tags FROM submissions"
    tag_rows = fetch_dataframe(query_tags)
    tags = set()
    for row in tag_rows["tags"].dropna():
        tags.update(t.strip() for t in row.split(","))

    authors = fetch_dataframe("SELECT DISTINCT author FROM submissions WHERE author IS NOT NULL")["author"].dropna().tolist()
    locations = fetch_dataframe("SELECT DISTINCT name FROM mrt_stations")["name"].dropna().tolist()

    return sorted(tags), authors, locations

def search_submissions(filters):
    query = """
        SELECT s.name, s.tags, s.price_tag, s.author, s.recommendations, s.date_submitted, ARRAY_AGG(ms.name) AS station_names
        FROM submissions s
        JOIN submission_stations ss ON s.id = ss.submission_id
        JOIN mrt_stations ms ON ss.station_id = ms.id
    """
    conditions = []
    params = {}

    if filters["name"]:
        conditions.append("s.name ILIKE :search_name")
        params["search_name"] = f"%{filters['name']}%"

    for i, tag in enumerate(filters["tags"]):
        conditions.append(f"s.tags ILIKE :tag{i}")
        params[f"tag{i}"] = f"%{tag}%"

    if filters["price"] and filters["price"] != "(Any)":
        conditions.append("s.price_tag = :price_tag")
        params["price_tag"] = filters["price"]

    if filters["author"] and filters["author"] != "(Any)":
        conditions.append("LOWER(s.author) = LOWER(:author)")
        params["author"] = filters["author"]

    if filters["location"] and filters["location"] != "(Any)":
        conditions.append("ms.name = :location")
        params["location"] = filters["location"]

    if filters["recommendations"]:
        conditions.append("s.recommendations ILIKE :recommendations")
        params["recommendations"] = f"%{filters['recommendations']}%"

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY s.id ORDER BY s.date_submitted DESC"

    return fetch_dataframe(query, params)