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

def show_admin_dashboard():

    df, forecast = load_data()

    df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")
    df = df.dropna(subset=["Claim_Submission_Date"])

    st.title("Executive Dashboard")

    dept_filter = st.selectbox(
        "Department",
        ["All"] + sorted(df["Department"].dropna().unique())
    )

    if dept_filter != "All":
        df = df[df["Department"] == dept_filter]

    total_revenue = df["Billing_Amount"].sum()
    approved_revenue = df["Approved_Amount"].sum()

    total_claims = len(df)
    approved_claims = (df["Denial_Flag"] == 0).sum()

    approval_rate = (approved_claims / total_claims) * 100 if total_claims else 0
    denial_rate = 100 - approval_rate
    leakage = total_revenue - approved_revenue

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total Revenue", format_inr(total_revenue))
    k2.metric("Approval Rate", f"{approval_rate:.2f}%")
    k3.metric("Denial Rate", f"{denial_rate:.2f}%")
    k4.metric("Revenue Leakage", format_inr(leakage))

    st.divider()

    trend = df.groupby(
        df["Claim_Submission_Date"].dt.to_period("M")
    )["Billing_Amount"].sum().reset_index()

    trend["Month"] = trend["Claim_Submission_Date"].astype(str)

    fig_trend = px.area(
        trend,
        x="Month",
        y="Billing_Amount",
        title="Monthly Revenue Trend"
    )

    fig_trend.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (₹)"
    )

    fig_trend.update_traces(
        hovertemplate="Month: %{x}<br>Revenue: ₹ %{y:,.0f}"
    )

    fig_forecast = go.Figure()

    fig_forecast.add_trace(
        go.Scatter(
            x=forecast["Month"],
            y=forecast["Forecasted_Revenue"],
            mode="lines",
            name="Forecast"
        )
    )

    fig_forecast.update_layout(
        title="Revenue Forecast",
        xaxis_title="Month",
        yaxis_title="Forecasted Revenue (₹)"
    )

    fig_forecast.update_traces(
        hovertemplate="Month: %{x}<br>Forecast: ₹ %{y:,.0f}"
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.plotly_chart(fig_forecast, use_container_width=True)

    st.divider()

    dept = df.copy()
    dept["Leakage"] = dept["Billing_Amount"] - dept["Approved_Amount"]

    dept_summary = dept.groupby("Department")["Leakage"].sum().reset_index()

    fig_waterfall = go.Figure(go.Waterfall(
        x=dept_summary["Department"],
        y=dept_summary["Leakage"],
        measure=["relative"] * len(dept_summary),
        name="Leakage"
    ))

    fig_waterfall.update_layout(
        title="Revenue Leakage by Department",
        xaxis_title="Department",
        yaxis_title="Leakage (₹)"
    )

    fig_waterfall.update_traces(
        hovertemplate="Department: %{x}<br>Leakage: ₹ %{y:,.0f}"
    )

    denial = df.groupby("Insurance_Type")["Denial_Flag"].mean().reset_index()
    denial["Denial_Rate"] = denial["Denial_Flag"] * 100

    fig_denial = px.funnel(
        denial,
        x="Denial_Rate",
        y="Insurance_Type",
        title="Denial Rate by Insurance Type"
    )

    fig_denial.update_layout(
        xaxis_title="Denial Rate (%)",
        yaxis_title="Insurance Type"
    )

    fig_denial.update_traces(
        hovertemplate="Insurance: %{y}<br>Denial: %{x:.2f}%"
    )

    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col4:
        st.plotly_chart(fig_denial, use_container_width=True)

    st.divider()

    fig_scatter = px.scatter(
        df,
        x="Billing_Amount",
        y="Approved_Amount",
        color="Denial_Flag",
        title="Billing vs Approved Amount (Anomaly View)"
    )

    fig_scatter.update_layout(
        xaxis_title="Billing Amount (₹)",
        yaxis_title="Approved Amount (₹)"
    )

    fig_scatter.update_traces(
        hovertemplate="Billing: ₹ %{x:,.0f}<br>Approved: ₹ %{y:,.0f}"
    )

    fig_box = px.box(
        df,
        x="Department",
        y="Billing_Amount",
        title="Revenue Distribution by Department"
    )

    fig_box.update_layout(
        xaxis_title="Department",
        yaxis_title="Revenue (₹)"
    )

    fig_box.update_traces(
        hovertemplate="Revenue: ₹ %{y:,.0f}"
    )

    col5, col6 = st.columns(2)

    with col5:
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col6:
        st.plotly_chart(fig_box, use_container_width=True)