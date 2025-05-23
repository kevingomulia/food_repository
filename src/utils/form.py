from datetime import datetime
from .validation import validate_input
from .db import insert_and_return_id, execute_write

def submit_recommendation(data):
    errors = validate_input(data["name"], data["author"])
    if errors:
        return errors, None

    cleaned_data = {
        "name": data["name"].strip(),
        "tags": ",".join(t.strip().lower() for t in data["tags"].split(",")),
        "price_tag": data["price_tag"],
        "author": data["author"].strip().lower(),
        "recommendations": data["recommendations"],
        "date_submitted": datetime.now().strftime("%Y-%m-%d")
    }

    submission_query = """
        INSERT INTO submissions (name, tags, price_tag, author, recommendations, date_submitted)
        VALUES (:name, :tags, :price_tag, :author, :recommendations, :date_submitted)
        RETURNING id
    """
    submission_id = insert_and_return_id(submission_query, cleaned_data)

    for station in data["stations"]:
        execute_write("""
            INSERT INTO submission_stations (submission_id, station_id)
            SELECT :submission_id, id FROM mrt_stations WHERE name = :station_name
        """, {"submission_id": submission_id, "station_name": station})

    return [], submission_id