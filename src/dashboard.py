import streamlit as st

from dashboards.admin_dashboard import show_admin_dashboard
from dashboards.finance_dashboard import show_finance_dashboard
from dashboards.analyst_dashboard import show_analyst_dashboard
from dashboards.department_dashboard import show_department_dashboard
from dashboards.doctor_dashboard import show_doctor_dashboard

from auth.login_page import login_screen
from ui.theme import apply_theme

st.set_page_config(
    page_title="Hospital Revenue Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_screen()
    st.stop()

apply_theme()

role = st.session_state["role"]
user = st.session_state["user"]["username"]

with st.sidebar:

    st.markdown(
        """
        <h2 style='text-align:center;'>🏥 Hospital Revenue Intelligence</h2>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        f"""
        <div style="
        background:rgba(30,41,59,0.4);
        padding:15px;
        border-radius:12px;
        margin-bottom:20px;
        text-align:center;
        border:1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(10px);
        ">
        <b>User</b><br>{user}<br><br>
        <b>Role</b><br>{role}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Navigation")

    if role == "admin":
        st.success("Admin Dashboard")

    elif role == "finance_manager":
        st.success("Finance Dashboard")

    elif role == "data_analyst":
        st.success("Data Analyst Dashboard")

    elif role == "department_head":
        st.success("Department Dashboard")

    elif role == "doctor":
        st.success("Doctor Dashboard")

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown(
    f"""
    <h1 style='font-size:34px; font-weight:600;'>
    Welcome back, {user}
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

if role == "admin":
    show_admin_dashboard()

elif role == "finance_manager":
    show_finance_dashboard()

elif role == "data_analyst":
    show_analyst_dashboard()

elif role == "department_head":
    show_department_dashboard()

elif role == "doctor":
    show_doctor_dashboard()

else:
    st.error("Role not recognized")