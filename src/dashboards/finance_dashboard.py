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

def show_finance_dashboard():

    df, forecast = load_data()

    st.markdown("## Financial Performance Dashboard")

    dept_filter = st.selectbox(
        "Department",
        ["All"] + sorted(df["Department"].dropna().unique())
    )

    if dept_filter != "All":
        df = df[df["Department"] == dept_filter]

    total_revenue = df["Billing_Amount"].sum()
    approved_revenue = df["Approved_Amount"].sum()
    payment_received = df["Payment_Received"].sum()

    leakage = total_revenue - approved_revenue
    total_claims = len(df)
    denied_claims = df["Denial_Flag"].sum() if "Denial_Flag" in df.columns else 0

    leakage_rate = (leakage / total_revenue) * 100 if total_revenue != 0 else 0
    collection_efficiency = (payment_received / total_revenue) * 100 if total_revenue != 0 else 0
    denial_rate = (denied_claims / total_claims) * 100 if total_claims > 0 else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
    c2.metric("Collection Efficiency", f"{collection_efficiency:.2f}%")
    c3.metric("Revenue Leakage", f"₹ {leakage:,.0f}")
    c4.metric("Denial Rate", f"{denial_rate:.2f}%")

    if leakage_rate > 10:
        st.warning("High revenue leakage detected")

    st.divider()

    fig_forecast = go.Figure()

    fig_forecast.add_trace(
        go.Scatter(
            x=forecast["Month"],
            y=forecast["Forecasted_Revenue"],
            mode="lines",
            name="Forecast"
        )
    )

    if "Lower_Bound" in forecast.columns and "Upper_Bound" in forecast.columns:
        fig_forecast.add_trace(
            go.Scatter(
                x=forecast["Month"],
                y=forecast["Upper_Bound"],
                line=dict(width=0),
                showlegend=False
            )
        )

        fig_forecast.add_trace(
            go.Scatter(
                x=forecast["Month"],
                y=forecast["Lower_Bound"],
                fill="tonexty",
                line=dict(width=0),
                name="Confidence Interval"
            )
        )

    fig_forecast.update_layout(
        title="Revenue Forecast",
        xaxis_title="Month",
        yaxis_title="Revenue (₹)"
    )

    fig_forecast.update_traces(
        hovertemplate="Month: %{x}<br>Revenue: ₹ %{y:,.0f}"
    )

    dept = df.groupby("Department").agg({
        "Billing_Amount": "sum",
        "Approved_Amount": "sum",
        "Payment_Received": "sum"
    }).reset_index()

    dept["Leakage"] = dept["Billing_Amount"] - dept["Approved_Amount"]

    fig_waterfall = go.Figure(go.Waterfall(
        x=dept["Department"],
        y=dept["Leakage"],
        measure=["relative"] * len(dept)
    ))

    fig_waterfall.update_layout(
        title="Revenue Leakage by Department",
        xaxis_title="Department",
        yaxis_title="Leakage (₹)"
    )

    fig_waterfall.update_traces(
        hovertemplate="Department: %{x}<br>Leakage: ₹ %{y:,.0f}"
    )

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.plotly_chart(fig_forecast, use_container_width=True)

    with col2:
        st.plotly_chart(fig_waterfall, use_container_width=True)

    st.divider()

    sample = df.sample(min(len(df), 3000))

    fig_scatter = px.scatter(
        sample,
        x="Billing_Amount",
        y="Approved_Amount",
        color="Department",
        title="Billing vs Approved Analysis"
    )

    fig_scatter.update_layout(
        xaxis_title="Billing Amount (₹)",
        yaxis_title="Approved Amount (₹)"
    )

    fig_scatter.update_traces(
        hovertemplate="Billing: ₹ %{x:,.0f}<br>Approved: ₹ %{y:,.0f}"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("Finance Data Sample"):
        st.dataframe(df.head(20))