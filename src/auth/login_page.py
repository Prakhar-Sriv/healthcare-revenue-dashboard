import streamlit as st
from auth.login import authenticate_user
import base64

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def login_screen():

    st.set_page_config(layout="wide")

    dna = get_base64("assets/dna.jpg")
    logo = get_base64("assets/medilytics_logo.png")

    st.markdown(f"""
    <style>

    #MainMenu {{visibility:hidden;}}
    footer {{visibility:hidden;}}
    header {{visibility:hidden;}}

    .stApp {{
        background: #020617;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: -10%;
        right: -10%;
        width: 120%;
        height: 120%;
        background: url("data:image/png;base64,{dna}") no-repeat;
        background-size: contain;
        background-position: top right;
        opacity: 0.10;
        transform: rotate(-35deg);
        pointer-events: none;
    }}

    /* REMOVE TOP GAP / BOX */
    .block-container {{
        padding-top: 0rem !important;
    }}

    /* CENTER */
    .main-center {{
        max-width: 320px;
        margin: auto;
        margin-top: 18vh;
        text-align: center;
    }}

    .logo {{
        width: 140px;
        margin-bottom: 10px;
    }}

    .login-title {{
        font-size: 22px;
        color: #14b8a6;
        margin-bottom: 15px;
        font-weight: 600;
    }}

    /* GLASS BOX */
    .glass-box {{
        padding: 20px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.25);
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
    }}

    div[data-testid="stTextInput"] {{
        width: 100%;
    }}

    .stTextInput input {{
        background: rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.15);
        border-radius:6px;
        padding:10px;
        color:white;
    }}

    /* BUTTON RIGHT ALIGN */
    .btn-right {{
        display: flex;
        justify-content: flex-end;
    }}

    .stButton>button {{
        background: linear-gradient(135deg,#14b8a6,#0ea5e9);
        border:none;
        height:36px;
        border-radius:6px;
        padding: 0 18px;
        margin-top:10px;
    }}

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-center">', unsafe_allow_html=True)

    st.markdown(f'<img src="data:image/png;base64,{logo}" class="logo"/>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Login</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-box">', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    st.markdown('<div class="btn-right">', unsafe_allow_html=True)
    login = st.button("Login")
    st.markdown('</div>', unsafe_allow_html=True)

    if login:
        user = authenticate_user(username, password)

        if user:
            st.session_state["user"] = user
            st.session_state["role"] = user["role"]
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)