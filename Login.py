import streamlit as st
import pandas as pd
from PIL import Image

def show_login():
    st.set_page_config(page_title="Medlytics Dashboard", layout="wide")

    # Load logo
    logo_path = r"C:\Users\Prakhar\Downloads\logo.png"
    logo = Image.open(logo_path)

    # Load users database
    users = pd.read_csv("users.csv")
  
    # Session states
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if "username" not in st.session_state:
        st.session_state.username = None

    if "department" not in st.session_state:
        st.session_state.department = None

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        if not st.session_state.logged_in:

            l1, l2, l3 = st.columns([1,2,1])

            with l2:
                st.image(logo)

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            st.write("")

            if st.button("Login", use_container_width=True):

                # Check credentials in CSV
                user = users[
                    (users["username"] == username) &
                    (users["password"] == password)
                ]

                if not user.empty:

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user.iloc[0]["role"]
                    st.session_state.department = user.iloc[0]["department"]

                    st.success("Login successful")
                    st.rerun()

                else:
                    st.error("Invalid Username or Password")

        else:

            st.success(f"Welcome {st.session_state.username}")

            role = st.session_state.role

            
