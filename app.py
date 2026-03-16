import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Revenue Leakage Analysis",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0B1626; 
        color: #FFFFFF;
    }
    
    /* SIDEBAR COLOR */
    [data-testid="stSidebar"] {
        background-color: #111B27 !important;
        border-right: 1px solid #1E2D40;
    }

    /* CENTERED TITLE */
    .main-title {
        text-align: center;
        color: #FFD700;
        font-size: 28px; 
        font-weight: 800;
        font-family: 'Arial', sans-serif;
        padding: 10px;
        text-transform: uppercase;
    }

    /* KPI BOXES */
    div[data-testid="metric-container"] {
        background-color: #16263A;
        border: 1px solid #243B55;
        border-radius: 10px;
        padding: 20px 15px; /* Increased top/bottom padding */
        text-align: center;
    }

    /* KPI LABELS - UPDATED FOR SHARPNESS & SIZE */
    [data-testid="stMetricLabel"] p {
        font-family: 'Arial Black', 'Arial', sans-serif !important;
        font-size: 16px !important; /* Larger size */
        font-weight: 900 !important; /* Maximum boldness */
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important; /* Prevents blurriness by spacing letters */
        margin-bottom: 8px !important;
    }

    /* VIBRANT COLORS FOR KPI LABELS */
    [data-testid="column"]:nth-child(1) [data-testid="stMetricLabel"] p { color: #00E5FF !important; } 
    [data-testid="column"]:nth-child(2) [data-testid="stMetricLabel"] p { color: #FF5E5E !important; } 
    [data-testid="column"]:nth-child(3) [data-testid="stMetricLabel"] p { color: #FFD700 !important; } 
    [data-testid="column"]:nth-child(4) [data-testid="stMetricLabel"] p { color: #00FF87 !important; }

    /* KPI VALUES */
    div[data-testid="stMetricValue"] div {
        color: white !important;
        font-size: 1.8rem !important; 
        font-weight: 800 !important;
        font-family: 'Arial', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

def apply_exact_sync_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF", family="Arial", size=12),
        margin=dict(l=40, r=20, t=30, b=40),
        legend=dict(font=dict(size=10, family="Arial"), bgcolor="rgba(0,0,0,0)")
    )
    fig.update_xaxes(
        tickfont=dict(size=12, color="#00D4FF", family="Arial"),
        showgrid=False,
        linecolor='#243B55'
    )
    fig.update_yaxes(
        tickfont=dict(size=12, color="#E0E0E0", family="Arial"),
        gridcolor="#1E2D40",
        showgrid=True
    )
    return fig

@st.cache_data
def load_data():
    # Ensure the file exists in your directory
    df = pd.read_csv("cleaned_claim_dataset.csv")
    df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"])
    df["Revenue_Leakage"] = (df["Expected_Revenue"] - df["Actual_Revenue"]).fillna(0)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

with st.sidebar:
    logo_path = "image"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: white;'>MEDILYTICS</h3>", unsafe_allow_html=True)
    st.divider()
    selected_dept = st.selectbox("Department", options=["All Departments"] + sorted(df["Department"].unique().tolist()))
    selected_ins = st.selectbox("Insurance", options=["All Insurance"] + sorted(df["Insurance_Type"].unique().tolist()))

filtered_df = df.copy()
if selected_dept != "All Departments":
    filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
if selected_ins != "All Insurance":
    filtered_df = filtered_df[filtered_df["Insurance_Type"] == selected_ins]

st.markdown('<div class="main-title">REVENUE LEAKAGE ANALYSIS</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.error("No Data Found")
else:
    # --- KPI BOXES ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Claims", f"{len(filtered_df):,}")
    k2.metric("Total Leakage", f"₹{filtered_df['Revenue_Leakage'].sum():,.0f}")
    k3.metric("Avg Leakage", f"₹{filtered_df['Revenue_Leakage'].mean():,.0f}")
    
    # Calculate Top Loss Dept safely
    top_dept = filtered_df.groupby("Department")["Revenue_Leakage"].sum().idxmax()
    k4.metric("Top Loss Dept", top_dept)

    st.divider()

    # --- CHARTS ---
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    # 1. Dept Bar
    with c1:
        st.markdown("<p style='color:#FFD700; font-weight:bold; font-size:20px;'>Leakage by Department</p>", unsafe_allow_html=True)
        dept_data = filtered_df.groupby("Department")["Revenue_Leakage"].sum().reset_index()
        fig1 = px.bar(dept_data, x="Revenue_Leakage", y="Department", orientation='h', color_discrete_sequence=['#3498DB'])
        st.plotly_chart(apply_exact_sync_style(fig1), use_container_width=True)

    # 2. Fill-Area Trend
    with c2:
        st.markdown("<p style='color:#FFD700; font-weight:bold; font-size:20px;'>Revenue Leakage Trend (Fill-Area)</p>", unsafe_allow_html=True)
        trend_df = filtered_df.copy()
        trend_df["Month"] = trend_df["Claim_Submission_Date"].dt.to_period("M").astype(str)
        trend_grouped = trend_df.groupby("Month")[["Revenue_Leakage", "Actual_Revenue"]].sum().reset_index()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_grouped["Month"], y=trend_grouped["Actual_Revenue"], fill='tozeroy', name='Actual', line=dict(color='#00D4FF')))
        fig2.add_trace(go.Scatter(x=trend_grouped["Month"], y=trend_grouped["Revenue_Leakage"], fill='tozeroy', name='Loss', line=dict(color='#FF4B4B')))
        st.plotly_chart(apply_exact_sync_style(fig2), use_container_width=True)

    # 3. Insurance Pie
    with c3:
        st.markdown("<p style='color:#FFD700; font-weight:bold; font-size:20px;'>Leakage by Insurance</p>", unsafe_allow_html=True)
        ins_data = filtered_df.groupby("Insurance_Type")["Revenue_Leakage"].sum().reset_index()
        fig3 = px.pie(ins_data, values="Revenue_Leakage", names="Insurance_Type", hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(apply_exact_sync_style(fig3), use_container_width=True)

    # 4. Distribution Histogram
    with c4:
        st.markdown("<p style='color:#FFD700; font-weight:bold; font-size:20px;'>Leakage Distribution</p>", unsafe_allow_html=True)
        fig4 = px.histogram(filtered_df, x="Revenue_Leakage", nbins=30, color_discrete_sequence=['#3498DB'])
        st.plotly_chart(apply_exact_sync_style(fig4), use_container_width=True)

    st.subheader("High-Leakage Claim Details")
    st.dataframe(filtered_df.sort_values(by="Revenue_Leakage", ascending=False).head(10), use_container_width=True)