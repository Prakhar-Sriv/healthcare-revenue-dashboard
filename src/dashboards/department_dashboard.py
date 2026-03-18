import streamlit as st
import pandas as pd
import plotly.express as px
import os
from ui.theme import style_chart

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "feature_store.csv"))
    return df

def show_department_dashboard():

    df = load_data()

    st.markdown("## Department Performance Dashboard")

    dept_filter = st.selectbox(
        "Select Department",
        ["All"] + sorted(df["Department"].dropna().unique())
    )

    if dept_filter != "All":
        df = df[df["Department"] == dept_filter]

    total_revenue = df["Billing_Amount"].sum()
    approved = df["Approved_Amount"].sum()
    leakage = total_revenue - approved

    total_claims = len(df)
    denied_claims = df["Denial_Flag"].sum() if "Denial_Flag" in df.columns else 0

    leakage_rate = (leakage / total_revenue) * 100 if total_revenue != 0 else 0
    denial_rate = (denied_claims / total_claims) * 100 if total_claims > 0 else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
    c2.metric("Revenue Leakage", f"₹ {leakage:,.0f}")
    c3.metric("Leakage Rate", f"{leakage_rate:.2f}%")
    c4.metric("Denial Rate", f"{denial_rate:.2f}%")

    if leakage_rate > 10:
        st.warning("High revenue leakage detected")

    st.divider()

    dept_summary = df.groupby("Department")["Billing_Amount"].sum().reset_index()

    fig_bar = px.bar(
        dept_summary.sort_values("Billing_Amount", ascending=False),
        x="Department",
        y="Billing_Amount",
        title="Total Revenue by Department"
    )

    fig_bar.update_layout(
        xaxis_title="Department",
        yaxis_title="Revenue (₹)"
    )

    fig_bar.update_traces(
        hovertemplate="Revenue: ₹ %{y:,.0f}"
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

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    sample = df.sample(min(len(df), 3000))

    fig_scatter = px.scatter(
        sample,
        x="Billing_Amount",
        y="Approved_Amount",
        color="Denial_Flag",
        title="Billing vs Approved Amount"
    )

    fig_scatter.update_layout(
        xaxis_title="Billing Amount (₹)",
        yaxis_title="Approved Amount (₹)"
    )

    fig_scatter.update_traces(
        hovertemplate="Billing: ₹ %{x:,.0f}<br>Approved: ₹ %{y:,.0f}"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("Department Data Sample"):
        st.dataframe(df.head(20))