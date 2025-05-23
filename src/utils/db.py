import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

@st.cache_resource
def get_engine():
    return create_engine(st.secrets["DATABASE_URL"])

def fetch_dataframe(query, params=None):
    with get_engine().connect() as conn:
        return pd.read_sql(text(query), conn, params=params)

def execute_write(query, params):
    with get_engine().begin() as conn:
        conn.execute(text(query), params)

def insert_and_return_id(query, params):
    with get_engine().begin() as conn:
        result = conn.execute(text(query), params)
        return result.scalar()