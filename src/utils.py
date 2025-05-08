# Import standard library modules
import hmac
import re

# Import third-party library modules
import streamlit as st


def _password_entered():
    if hmac.compare_digest(st.session_state["app_password"], st.secrets["APP_PWD"]):
        st.session_state["password_correct"] = True
        del st.session_state["app_password"]
    else:
        st.session_state["password_correct"] = False


def check_password():
    """
    Based on https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso
    """
    if st.secrets.get("APP_PWD") is None or st.session_state.get(
        "password_correct", False
    ):
        return True

    st.text_input(
        "Password",
        type="password",
        on_change=_password_entered,
        key="app_password",
    )

    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")

    return False

def sanitize_tags(tags_string):
    """Sanitize tags input to prevent potential SQL injection"""
    if not tags_string:
        return ""
    # Only allow alphanumeric, commas, spaces, and hyphens
    clean_tags = re.sub(r'[^\w\s,-]', '', tags_string)
    return clean_tags

def validate_input(name, author):
    """Validate user input"""
    errors = []
    
    if len(name) < 2:
        errors.append("Name must be at least 2 characters")
    
    if author and len(author) < 2:
        errors.append("Author name must be at least 2 characters")
    
    return errors

# https://code-editor-documentation.streamlit.app/Advanced_usage#custom-buttons
RUN_BUTTON = {
    "name": "Run",
    "feather": "Play",
    "primary": True,
    "hasText": True,
    "showWithIcon": True,
    "commands": ["submit"],
    "alwaysOn": True,
    "style": {"bottom": "0.44rem", "right": "0.4rem"},
}
