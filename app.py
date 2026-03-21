import streamlit as st
from Login import show_login
from Executive_Dashboard import show_dashboard

st.set_page_config(page_title="Medilytics", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Navigation logic
if not st.session_state.logged_in:
    show_login()

else:
    show_dashboard()
