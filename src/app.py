import streamlit as st
import pandas as pd
from utils.db import fetch_dataframe
from utils.form import submit_recommendation
from utils.search import get_filter_options, search_submissions

st.set_page_config(page_title="🍜 The Pot and Ladle", layout="wide", initial_sidebar_state="expanded")

def render_submit_tab():
    st.subheader("📝 Submit a New Food Recommendation")
    locations = fetch_dataframe("SELECT DISTINCT name FROM mrt_stations")["name"].dropna().tolist()

    with st.form("submit_form"):
        data = {
            "name": st.text_input("Food Place Name", max_chars=250),
            "tags": st.text_input("Cuisine Tags (comma-separated)", placeholder="e.g. Chinese, Vegetarian"),
            "price_tag": st.selectbox("Price Tag", ["$", "$$", "$$$", "$$$$+"]),
            "author": st.text_input("Your Name"),
            "stations": st.multiselect("Nearby MRT Stations (max 2)", locations),
            "recommendations": st.text_area("Recommendations (optional)", max_chars=500)
        }

        if len(data["stations"]) > 2:
            st.error("Please select a maximum of 2 MRT stations.")
            data["stations"] = data["stations"][:2]

        if st.form_submit_button("Submit"):
            if not data["name"] or not data["stations"]:
                st.error("Please provide at least a name and one MRT station.")
            else:
                errors, _ = submit_recommendation(data)
                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    st.success("🎉 Recommendation submitted successfully!")

def render_search_tab():
    st.subheader("🔍 Search Food Recommendations")
    tags, authors, locations = get_filter_options()

    filters = {
        "name": st.sidebar.text_input("Search by Name"),
        "tags": st.sidebar.multiselect("Tags", tags),
        "price": st.sidebar.selectbox("Price Tag", ["(Any)", "$", "$$", "$$$", "$$$$+"]),
        "author": st.sidebar.selectbox("Author", ["(Any)"] + authors),
        "location": st.sidebar.selectbox("Nearest MRT", ["(Any)"] + locations),
        "recommendations": st.sidebar.text_input("Search by Food Items")
    }

    results = search_submissions(filters)
    results = results.rename(columns={
        "name": "Name",
        "tags": "Tags",
        "price_tag": "Price",
        "author": "Author",
        "recommendations": "Food Item Recommendations",
        "date_submitted": "Date Submitted",
        "station_names": "Nearby MRT Stations"
    })

    st.write(f"{len(results)} submissions found")
    st.dataframe(results, use_container_width=True, hide_index=True)

def main():
    st.title("🍜 The Pot and Ladle")
    tab1, tab2 = st.tabs(["📝 Submit Recommendation", "🔍 Get Recommendation"])
    with tab1:
        render_submit_tab()
    with tab2:
        render_search_tab()

if __name__ == "__main__":
    main()