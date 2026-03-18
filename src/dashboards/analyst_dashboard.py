import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from ui.theme import style_chart

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "feature_store.csv"))
    forecast = pd.read_csv(os.path.join(DATA_DIR, "revenue_forecast.csv"))
    return df, forecast

def format_inr(num):
    num = float(num)
    if num >= 10000000:
        return f"₹ {num/10000000:.2f} Cr"
    if num >= 100000:
        return f"₹ {num/100000:.2f} L"
    return f"₹ {num:,.0f}"

def show_analyst_dashboard():

    df, forecast = load_data()

    df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")
    df = df.dropna(subset=["Claim_Submission_Date"])

    st.title("Data Analyst Dashboard")

    dept_filter = st.selectbox(
        "Department",
        ["All"] + sorted(df["Department"].dropna().unique())
    )

    if dept_filter != "All":
        df = df[df["Department"] == dept_filter]

    total_claims = len(df)
    anomaly_rate = df["Denial_Flag"].mean() * 100 if "Denial_Flag" in df.columns else 0
    avg_revenue = df["Billing_Amount"].mean()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Claims", f"{total_claims:,}")
    c2.metric("Denial Rate", f"{anomaly_rate:.2f}%")
    c3.metric("Avg Revenue", format_inr(avg_revenue))

    st.divider()

    trend = df.groupby(
        df["Claim_Submission_Date"].dt.to_period("M")
    )["Billing_Amount"].sum().reset_index()

    trend["Month"] = trend["Claim_Submission_Date"].astype(str)

    fig_trend = px.area(
        trend,
        x="Month",
        y="Billing_Amount",
        title="Revenue Trend Analysis"
    )

    fig_trend.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (₹)"
    )

    fig_trend.update_traces(
        hovertemplate="Month: %{x}<br>Revenue: ₹ %{y:,.0f}"
    )

    sample = df.sample(min(len(df), 3000))

    fig_scatter = px.scatter(
        sample,
        x="Billing_Amount",
        y="Approved_Amount",
        color="Denial_Flag",
        title="Billing vs Approved (Anomaly Detection)"
    )

    fig_scatter.update_layout(
        xaxis_title="Billing Amount (₹)",
        yaxis_title="Approved Amount (₹)"
    )

    fig_scatter.update_traces(
        hovertemplate="Billing: ₹ %{x:,.0f}<br>Approved: ₹ %{y:,.0f}"
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    fig_hist = px.histogram(
        df,
        x="Billing_Amount",
        nbins=40,
        title="Revenue Distribution"
    )

    fig_hist.update_layout(
        xaxis_title="Billing Amount (₹)",
        yaxis_title="Frequency"
    )

    fig_box = px.box(
        df,
        x="Department",
        y="Billing_Amount",
        title="Outlier Detection by Department"
    )

    fig_box.update_layout(
        xaxis_title="Department",
        yaxis_title="Revenue (₹)"
    )

    fig_box.update_traces(
        hovertemplate="Revenue: ₹ %{y:,.0f}"
    )

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.plotly_chart(fig_hist, use_container_width=True)

    with col4:
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    numeric_df = df.select_dtypes(include=["number"]).corr()

    fig_heatmap = px.imshow(
        numeric_df,
        text_auto=True,
        title="Feature Correlation Matrix"
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    with st.expander("Sample Data"):
        st.dataframe(df.head(20))