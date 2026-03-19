import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os


# 1. PAGE CONFIGURATION & STANDALONE CSS

st.set_page_config(page_title="Department Dashboard", layout="wide", initial_sidebar_state="expanded")

# High-Contrast Premium SaaS CSS (EXACTLY AS REQUESTED)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
        color: #ffffff !important;
    }
    
    .stApp { 
        background-color: #0f172a; 
        background-image: 
            radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.15) 0px, transparent 50%), 
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 50%);
        background-attachment: fixed; 
    }

    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.1); 
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Keep sidebar selectbox readable (fix white text on light select background) */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSelectbox p {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div > div > div {
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] input,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {
        color: #0f172a !important;
        fill: #0f172a !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] * {
        color: #0f172a !important;
        fill: #0f172a !important;
        opacity: 1 !important;
    }

    /* Expander label + content text visibility */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary div {
        color: #ffffff !important;
        background: #1e293b !important;
    }
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpanderToggleIcon"] {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    [data-testid="stExpanderDetails"],
    [data-testid="stExpanderDetails"] * {
        color: #ffffff !important;
    }
    [data-testid="stExpander"] {
        background: #1e293b !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpanderDetails"] {
        background: #1e293b !important;
    }

    /* Dataframe theme alignment */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] [role="grid"],
    [data-testid="stDataFrame"] [role="row"],
    [data-testid="stDataFrame"] [role="gridcell"] {
        background: #1e293b !important;
        color: #ffffff !important;
    }
    [data-testid="stDataFrame"] [role="columnheader"] {
        background: #0f172a !important;
        color: #e2e8f0 !important;
        border-bottom: 1px solid rgba(255,255,255,0.25) !important;
    }

    /* Dataframe action controls (search/download/menu) visibility */
    [data-testid="stDataFrame"] button,
    [data-testid="stDataFrame"] [role="button"] {
        color: #ffffff !important;
        background: #1e293b !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
    }
    [data-testid="stDataFrame"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    [data-testid="stDataFrame"] input {
        color: #ffffff !important;
        background: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
    }

    .chart-container { 
        background: rgba(30, 41, 59, 0.8); 
        border-radius: 16px; 
        padding: 1.5rem; 
        border: 1px solid rgba(255, 255, 255, 0.15); 
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4); 
        margin-bottom: 0.5rem; 
        backdrop-filter: blur(10px);
        color: #ffffff;
    }

    /* Apply same visual treatment to st.container(border=True) blocks */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        border: 4px solid rgba(255, 255, 255, 1) !important;
        outline: 4px solid rgba(255, 255, 255, 1) !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255,255,255,0.12) !important;
        margin-bottom: 0.5rem !important;
        backdrop-filter: blur(10px) !important;
    }

    .custom-kpi {
        padding: 24px 20px;
        border-radius: 12px;
        color: #ffffff;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .custom-kpi:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 25px rgba(0, 0, 0, 0.5);
    }
    .custom-kpi .kpi-title {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.95;
        margin-bottom: 8px;
    }
    .custom-kpi .kpi-value {
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    
    .bg-blue { background: linear-gradient(135deg, #0ea5e9 0%, #1d4ed8 100%); }
    .bg-red { background: linear-gradient(135deg, #f43f5e 0%, #be123c 100%); }
    .bg-purple { background: linear-gradient(135deg, #a855f7 0%, #6d28d9 100%); }
    .bg-green { background: linear-gradient(135deg, #10b981 0%, #047857 100%); }
</style>
""", unsafe_allow_html=True)


# 2. REAL DATA LOADER

@st.cache_data
def load_data():
    """Dynamically locates the 'data' folder and loads feature_store.csv"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = None
    
    for _ in range(4):
        potential_dir = os.path.join(current_dir, "data")
        if os.path.exists(potential_dir):
            data_dir = potential_dir
            break
        current_dir = os.path.dirname(current_dir)
        
    if not data_dir or not os.path.exists(data_dir):
        data_dir = os.path.join(os.getcwd(), "data")
        
    feature_store_path = os.path.join(data_dir, "feature_store.csv")
    
    if not os.path.exists(feature_store_path):
        st.error(f"Data Source Error: Missing files in {data_dir}. Please ensure feature_store.csv exists.")
        st.stop()
        
    df = pd.read_csv(feature_store_path)

    # Safe mapping for the Time-Series chart
    if "Claim_Submission_Date" in df.columns:
        df["Claim_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")
    elif "Claim_Date" not in df.columns:
        df["Claim_Date"] = pd.to_datetime("today") 
        
    # Safe mapping for the Donut chart (Fixed integer concatenation error)
    if "Denial_Reason" not in df.columns:
        if "Insurance_Type" in df.columns:
            df["Denial_Reason"] = "Type " + df["Insurance_Type"].astype(str) + " Error"
        else:
            df["Denial_Reason"] = "System Review Needed"

    df = df.dropna(subset=["Claim_Date"])
    return df


# 3. HELPER FUNCTIONS

def format_inr(num):
    if num >= 10000000:
        return f"INR {num/10000000:.2f} Cr"
    if num >= 100000:
        return f"INR {num/100000:.2f} L"
    return f"INR {num:,.0f}"

def get_chart_layout(title=""):
    """Standardized Plotly theme with pure white text."""
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0"),
        margin=dict(l=10, r=10, t=4, b=20),
        hoverlabel=dict(bgcolor="#0f172a", font_size=14, font_family="Plus Jakarta Sans", font_color="#ffffff"),
        legend=dict(
            font=dict(color="#ffffff", size=12),
            bgcolor="rgba(15, 23, 42, 0.85)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
        )
    )


# 4. MAIN DASHBOARD FUNCTION

def show_department_dashboard():
    df = load_data()

    # Dashboard Header
    st.markdown(
        """
        <div style="padding-bottom: 25px;">
            <h1 style='font-size:36px; font-weight:800; color: #ffffff; margin-bottom: 5px; letter-spacing: -1px;'>
                Department Performance Dashboard
            </h1>
            <p style='color: #cbd5e1; font-size: 16px; font-weight: 500;'>Unit-level financial efficiency, revenue trends, and leakage tracking.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar Filter
    st.sidebar.markdown('<div style="font-size:14px; font-weight:700; color:#ffffff; margin-top:15px; margin-bottom:10px; text-transform:uppercase; letter-spacing:1px;">Data Filters</div>', unsafe_allow_html=True)
    dept_filter = st.sidebar.selectbox(
        "Select Department",
        ["All"] + sorted(df["Department"].dropna().unique())
    )

    if dept_filter != "All":
        df = df[df["Department"] == dept_filter]

    # Calculate KPIs
    total_revenue = df["Billing_Amount"].sum()
    approved = df["Approved_Amount"].sum()
    leakage = total_revenue - approved
    total_claims = len(df)
    denied_claims = (df["Denial_Flag"] == 1).sum() if "Denial_Flag" in df.columns else 0

    leakage_rate = (leakage / total_revenue) * 100 if total_revenue != 0 else 0
    denial_rate = (denied_claims / total_claims) * 100 if total_claims > 0 else 0

    # Render Custom High-Contrast KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="custom-kpi bg-blue"><div class="kpi-title">Total Billed Revenue</div><div class="kpi-value">{format_inr(total_revenue)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="custom-kpi bg-red"><div class="kpi-title">Revenue Leakage</div><div class="kpi-value">{format_inr(leakage)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="custom-kpi bg-purple"><div class="kpi-title">Leakage Rate</div><div class="kpi-value">{leakage_rate:.2f}%</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="custom-kpi bg-green"><div class="kpi-title">Denial Rate</div><div class="kpi-value">{denial_rate:.2f}%</div></div>', unsafe_allow_html=True)


    # 5. CHARTS: TRENDS & ROOT CAUSES
  
    col_t1, col_t2 = st.columns([5, 5], gap="large")
    
    with col_t1:
        with st.container(border=True):
            st.markdown("<h3 style='margin:0 0 10px 0; color:#ffffff; font-size:20px; font-weight:700;'>Revenue Realization Trend (Weekly)</h3>", unsafe_allow_html=True)
            trend_df = df.set_index('Claim_Date')[['Billing_Amount', 'Approved_Amount']].resample('W').sum().reset_index()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=trend_df['Claim_Date'], y=trend_df['Billing_Amount'], name='Billed', fill='tozeroy', line=dict(color='#0ea5e9', width=3), fillcolor='rgba(14, 165, 233, 0.2)'))
            fig_trend.add_trace(go.Scatter(x=trend_df['Claim_Date'], y=trend_df['Approved_Amount'], name='Approved', fill='tozeroy', line=dict(color='#10b981', width=3), fillcolor='rgba(16, 185, 129, 0.2)'))
            fig_trend.update_layout(**get_chart_layout(""))
            fig_trend.update_layout(
                legend=dict(
                    x=0.99,
                    y=0.01,
                    xanchor="right",
                    yanchor="bottom",
                    font=dict(color="#ffffff", size=11),
                    bgcolor="rgba(15, 23, 42, 0.85)",
                    bordercolor="rgba(255,255,255,0.2)",
                    borderwidth=1,
                )
            )
            fig_trend.update_xaxes(showgrid=False, title="")
            fig_trend.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", title="Amount (INR)")
            st.plotly_chart(fig_trend, use_container_width=True)

    with col_t2:
        with st.container(border=True):
            st.markdown('<h3 style=\'margin:0 0 10px 0; color:#ffffff; font-size:17px; font-weight:700;\'>Root Cause: Claim Denials</h3>', unsafe_allow_html=True)
            denial_df = df[df['Denial_Flag'] == 1]['Denial_Reason'].value_counts().reset_index() if 'Denial_Flag' in df.columns else pd.DataFrame(columns=['Denial_Reason', 'Count'])
            
            if not denial_df.empty:
                denial_df.columns = ['Denial_Reason', 'Count']
                fig_donut = px.pie(denial_df, values='Count', names='Denial_Reason', hole=0.6, color_discrete_sequence=px.colors.sequential.Sunsetdark)
                fig_donut.update_layout(**get_chart_layout(""))
                fig_donut.update_layout(
                    showlegend=True,
                    legend=dict(
                        x=1.02,
                        y=0.95,
                        xanchor="left",
                        yanchor="top",
                        font=dict(color="#ffffff", size=12),
                        bgcolor="rgba(15, 23, 42, 0.85)",
                        bordercolor="rgba(255,255,255,0.2)",
                        borderwidth=1,
                    ),
                    margin=dict(r=165),
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#0f172a', width=2)))
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No denied claims found in this segment.")


    # 6. DEPARTMENTAL BREAKDOWN

    col1, col2 = st.columns([5, 5], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("<h3 style='margin:0 0 10px 0; color:#ffffff; font-size:17px; font-weight:700;'>Total Revenue Generation by Department</h3>", unsafe_allow_html=True)
            dept_summary = df.groupby("Department")["Billing_Amount"].sum().reset_index()
            fig_bar = px.bar(dept_summary.sort_values("Billing_Amount", ascending=True), y="Department", x="Billing_Amount", orientation='h')
            fig_bar.update_traces(marker_color='#a855f7') 
            fig_bar.update_layout(**get_chart_layout(""))
            fig_bar.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.15)", title="Revenue (INR)")
            fig_bar.update_yaxes(title="", tickfont=dict(color="#ffffff", size=13))
            st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='margin:0 0 10px 0; color:#ffffff; font-size:17px; font-weight:700;'>Billing vs Approved Amount Correlation</h3>", unsafe_allow_html=True)
            scatter_df = df.sample(min(len(df), 1500)).copy()
            if "Denial_Flag" in scatter_df.columns:
                scatter_df["Claim_Status"] = scatter_df["Denial_Flag"].map({0: "Approved", 1: "Denied"})
            else:
                scatter_df["Claim_Status"] = "Unknown"

            fig_scatter = px.scatter(
                scatter_df,
                x="Billing_Amount",
                y="Approved_Amount",
                color="Claim_Status",
                opacity=0.8,
                color_discrete_map={"Approved": "#10b981", "Denied": "#f43f5e"},
            )
            fig_scatter.update_layout(**get_chart_layout(""))
            fig_scatter.update_layout(
                legend_title_text="",
                legend=dict(
                    x=0.01,
                    y=0.99,
                    xanchor="left",
                    yanchor="top",
                    font=dict(color="#ffffff", size=11),
                    bgcolor="rgba(15, 23, 42, 0.85)",
                    borderwidth=0,
                )
            )
            fig_scatter.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.15)", title="Billed Amount (INR)")
            fig_scatter.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.15)", title="Approved Amount (INR)")
            st.plotly_chart(fig_scatter, use_container_width=True)

    # Raw Data Table
    with st.expander("View Raw Departmental Transactions (Last 50 Records)"):
        display_df = df.copy()
        if "Claim_Date" in display_df.columns:
            display_df['Claim_Date'] = display_df['Claim_Date'].dt.strftime('%Y-%m-%d')
        
        styled_table = (
            display_df.tail(50)
            .style
            .set_properties(**{
                "color": "#ffffff",
                "background-color": "#1e293b",
                "border-color": "rgba(255,255,255,0.15)",
            })
            .set_table_styles([
                {
                    "selector": "th",
                    "props": [
                        ("color", "#ffffff"),
                        ("background-color", "#1e293b"),
                        ("border", "1px solid rgba(255,255,255,0.2)"),
                    ],
                },
                {
                    "selector": "th.col_heading, th.row_heading, th.blank",
                    "props": [
                        ("color", "#ffffff"),
                        ("background-color", "#1e293b"),
                        ("border", "1px solid rgba(255,255,255,0.2)"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("color", "#ffffff"),
                        ("background-color", "#1e293b"),
                        ("border", "1px solid rgba(255,255,255,0.12)"),
                    ],
                },
            ])
        )
        st.dataframe(styled_table, use_container_width=True, hide_index=True)

# if __name__ == "__main__":
#     show_department_dashboard()
