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

def show_doctor_dashboard():

    df = load_data()

    st.markdown("## Doctor Performance Dashboard")

    proc_filter = st.selectbox(
        "Procedure Code",
        ["All"] + sorted(df["Procedure_Code"].dropna().unique())
    )

    if proc_filter != "All":
        df = df[df["Procedure_Code"] == proc_filter]

    total_billing = df["Billing_Amount"].sum()
    total_approved = df["Approved_Amount"].sum()

    total_claims = len(df)
    denied_claims = df["Denial_Flag"].sum() if "Denial_Flag" in df.columns else 0

    approval_rate = (total_approved / total_billing) * 100 if total_billing != 0 else 0

    procedures = df["Procedure_Code"].nunique()
    avg_revenue_per_proc = (total_billing / procedures) if procedures else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Billing", f"₹ {total_billing:,.0f}")
    c2.metric("Approved Amount", f"₹ {total_approved:,.0f}")
    c3.metric("Approval Rate", f"{approval_rate:.2f}%")
    c4.metric("Avg Revenue / Procedure", f"₹ {avg_revenue_per_proc:,.0f}")

    st.divider()

    proc_summary = df.groupby("Procedure_Code")["Billing_Amount"].sum().reset_index()

    fig_bar = px.bar(
        proc_summary.sort_values("Billing_Amount", ascending=False),
        x="Procedure_Code",
        y="Billing_Amount",
        title="Revenue by Procedure"
    )

    fig_bar.update_layout(
        xaxis_title="Procedure",
        yaxis_title="Revenue (₹)"
    )

    fig_bar.update_traces(
        hovertemplate="Revenue: ₹ %{y:,.0f}"
    )

    sample = df.sample(min(len(df), 3000))

    fig_scatter = px.scatter(
        sample,
        x="Billing_Amount",
        y="Approved_Amount",
        color="Procedure_Code",
        title="Billing vs Approved Comparison"
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
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    fig_hist = px.histogram(
        df,
        x="Billing_Amount",
        nbins=40,
        title="Billing Distribution"
    )

    fig_hist.update_layout(
        xaxis_title="Billing Amount (₹)",
        yaxis_title="Frequency"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    with st.expander("Sample Data"):
        st.dataframe(df.head(20))