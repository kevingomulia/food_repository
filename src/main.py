# Import third-party library modules
import streamlit as st
import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

# run this before importing local modules
st.set_page_config(
    page_title="🍜 The Pot and Ladle",
    page_icon=":material/code:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import local modules
import utils
load_dotenv()

# Database config
DATABASE_URL = os.getenv("DB_LOCAL_URL")
# DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def main():
    st.title("🍜 The Pot and Ladle")
    if not utils.check_password():
        st.stop()
    # Change background color for the tags
    st.markdown("""
        <style>
        .stMultiSelect [data-baseweb="tag"] {
            background-color: #d0e0ff !important;  /* Soft blue-gray */
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Submit Recommendation", "🔍 Get Recommendation"])

    # --- Tab 1: Submit Recommendation ---
    with tab1:
        st.subheader("📝 Submit a New Food Recommendation")

        # Fetch MRT station options
        with engine.connect() as conn:
            locations = pd.read_sql("SELECT DISTINCT name FROM mrt_stations", conn)['name'].dropna().tolist()

        with st.form("submit_form"):
            name = st.text_input("Food Place Name", max_chars=250)
            tags = st.text_input("Tags (comma-separated) (e.g. japanese, cafe, dessert)")
            price_tag = st.selectbox("Price Tag", ["$", "$$", "$$$", "$$$$+"])
            author = st.text_input("Your Name")
            selected_stations = st.multiselect("Nearby MRT Stations (max 2)", locations)

            submitted = st.form_submit_button("Submit")

            if submitted:
                if not name or not selected_stations:
                    st.error("Please provide at least a name and one MRT station.")
                else:
                    # Validate inputs
                    validation_errors = utils.validate_input(name, author)
                    if validation_errors:
                        for error in validation_errors:
                            st.error(error)
                    else:
                        # Sanitize inputs
                        name = name.strip()
                        tags = tags.strip().lower()
                        author = author.strip().lower()  # Convert author to lowercase
                        
                        date_now = datetime.now().strftime("%Y-%m-%d")

                        with engine.begin() as conn:
                            result = conn.execute(
                                text("INSERT INTO submissions (name, tags, price_tag, author, date_submitted) VALUES (:name, :tags, :price_tag, :author, :date_submitted) RETURNING id"),
                                {"name": name, "tags": tags, "price_tag": price_tag, "author": author, "date_submitted": date_now}
                            )
                            submission_id = result.scalar()

                            for station in selected_stations:
                                conn.execute(
                                    text("""
                                        INSERT INTO submission_stations (submission_id, station_id)
                                        SELECT :submission_id, id FROM mrt_stations WHERE name = :station_name
                                    """),
                                    {"submission_id": submission_id, "station_name": station}
                                )

                        st.success("🎉 Recommendation submitted successfully!")

    # --- Tab 2: Get Recommendation ---
    with tab2:
        with engine.connect() as conn:
            # Extract all unique tags
            tags_result = conn.execute(text("SELECT tags FROM submissions"))
            all_tags = set()
            for row in tags_result:
                if row.tags:
                    all_tags.update(tag.strip() for tag in row.tags.split(','))
            all_tags = sorted(all_tags)

            authors = pd.read_sql("SELECT DISTINCT author FROM submissions WHERE author IS NOT NULL", conn)['author'].dropna().tolist()
            locations = pd.read_sql("SELECT DISTINCT name FROM mrt_stations", conn)['name'].dropna().tolist()

        search_name = st.sidebar.text_input("Search by Name")
        selected_tags = st.sidebar.multiselect("Tags", all_tags)
        selected_price = st.sidebar.selectbox("Price Tag", ["(Any)", "$", "$$", "$$$", "$$$$+"])
        selected_author = st.sidebar.selectbox("Author", ["(Any)"] + authors)
        selected_location = st.sidebar.selectbox("Nearest MRT", ["(Any)"] + locations)

        query = """
        SELECT s.name, s.tags, s.price_tag, s.author, s.date_submitted, ARRAY_AGG(ms.name) AS station_names
        FROM submissions s
        JOIN submission_stations ss ON s.id = ss.submission_id
        JOIN mrt_stations ms ON ss.station_id = ms.id
        """
        conditions = []
        params = {}

        if search_name:
            conditions.append("s.name ILIKE :search_name")
            params["search_name"] = f"%{search_name}%"

        if selected_tags:
            for i, tag in enumerate(selected_tags):
                conditions.append(f"s.tags ILIKE :tag{i}")
                params[f"tag{i}"] = f"%{tag}%"

        if selected_price != "(Any)":
            conditions.append("s.price_tag = :price_tag")
            params["price_tag"] = selected_price

        if selected_author != "(Any)":
            conditions.append("s.author = :author")
            params["author"] = selected_author

        if selected_location != "(Any)":
            conditions.append("ms.name = :location")
            params["location"] = selected_location

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY s.id ORDER BY s.date_submitted DESC"

        with engine.connect() as conn:
            results = pd.read_sql(text(query), conn, params=params)

        results = results.rename(columns={
            "name": "Name",
            "tags": "Tags",
            "price_tag": "Price",
            "author": "Author",
            "date_submitted": "Date Submitted",
            "station_names": "Nearby MRT Stations"
        })

        st.subheader("🔍 Search Results")
        st.write(f"{len(results)} submissions found")
        st.dataframe(results, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()