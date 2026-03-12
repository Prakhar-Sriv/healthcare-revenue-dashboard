import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Hospital Revenue Intelligence Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "feature_store.csv"))
    forecast = pd.read_csv(os.path.join(DATA_DIR, "revenue_forecast.csv"))
    core_metrics = pd.read_csv(os.path.join(DATA_DIR, "core_hospital_metrics.csv"))
    return df, forecast, core_metrics

df, forecast, core_metrics = load_data()

df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")
df = df.dropna(subset=["Claim_Submission_Date"])

department_map = {
0:"Cardiology",
1:"Orthopedics",
2:"Surgery",
3:"General Medicine",
4:"Neurology"
}

insurance_map = {
0:"Private Insurance",
1:"Government Scheme",
2:"Corporate Insurance",
3:"Self Pay",
4:"Insurance Partner"
}

if df["Department"].dtype != "object":
    df["Department"] = df["Department"].map(department_map)

if df["Insurance_Type"].dtype != "object":
    df["Insurance_Type"] = df["Insurance_Type"].map(insurance_map)

dept_colors = {
"Cardiology":"#1f77b4",
"Orthopedics":"#ff7f0e",
"Surgery":"#2ca02c",
"General Medicine":"#d62728",
"Neurology":"#9467bd"
}

def format_inr(num):
    num = float(num)
    if num >= 10000000:
        return f"₹ {num/10000000:.2f} Cr"
    if num >= 100000:
        return f"₹ {num/100000:.2f} L"
    return f"₹ {num:,.0f}"

st.title("Revenue Integrity & Predictive Financial Intelligence System")

total_revenue = df["Billing_Amount"].sum()
approved_revenue = df["Approved_Amount"].sum()
leakage = total_revenue - approved_revenue
leakage_percent = (leakage / total_revenue) * 100 if total_revenue != 0 else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", format_inr(total_revenue))
c2.metric("Approved Revenue", format_inr(approved_revenue))
c3.metric("Revenue Leakage", format_inr(leakage))
c4.metric("Leakage %", f"{leakage_percent:.2f}%")

st.subheader("Revenue Cycle Performance")

denial_rate = core_metrics["Denial_Rate"][0]
collection_efficiency = core_metrics["Average_Collection_Efficiency"][0]
revenue_realization = core_metrics["Average_Revenue_Realization_Rate"][0]
claim_processing_time = core_metrics["Average_Claim_Processing_Time"][0]

m1, m2, m3, m4 = st.columns(4)

m1.metric("Denial Rate", f"{denial_rate:.2f}%")
m2.metric("Collection Efficiency", f"{collection_efficiency:.2f}%")
m3.metric("Revenue Realization", f"{revenue_realization:.2f}%")
m4.metric("Claim Processing Time", f"{claim_processing_time:.1f} Days")

st.sidebar.header("Filters")

department = st.sidebar.multiselect("Department", sorted(df["Department"].dropna().unique()))
insurance = st.sidebar.multiselect("Insurance Type", sorted(df["Insurance_Type"].dropna().unique()))

filtered_df = df.copy()

if department:
    filtered_df = filtered_df[filtered_df["Department"].isin(department)]

if insurance:
    filtered_df = filtered_df[filtered_df["Insurance_Type"].isin(insurance)]

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()

st.subheader("Monthly Revenue Trend")

trend = filtered_df.groupby(
filtered_df["Claim_Submission_Date"].dt.to_period("M")
)["Billing_Amount"].sum().reset_index()

trend["Month"] = trend["Claim_Submission_Date"].astype(str)

fig1 = px.area(
trend,
x="Month",
y="Billing_Amount"
)

fig1.update_yaxes(tickformat=",", title="Revenue (₹)")

st.plotly_chart(fig1, use_container_width=True)

st.subheader("Revenue Forecast")

fig_forecast = px.line(
forecast,
x="Month",
y="Forecasted_Revenue",
markers=True
)

fig_forecast.update_traces(line=dict(dash="dash"))
fig_forecast.update_yaxes(tickformat=",", title="Forecasted Revenue (₹)")

st.plotly_chart(fig_forecast, use_container_width=True)

st.subheader("Revenue Leakage Rate by Department")

dept_analysis = filtered_df.copy()

dept_analysis["Leakage"] = (
dept_analysis["Billing_Amount"] -
dept_analysis["Approved_Amount"]
)

dept_summary = dept_analysis.groupby("Department").agg({
"Billing_Amount":"sum",
"Leakage":"sum"
}).reset_index()

dept_summary["Leakage_Rate"] = (
dept_summary["Leakage"] /
dept_summary["Billing_Amount"].replace(0, pd.NA)
) * 100

dept_summary = dept_summary.dropna()
dept_summary = dept_summary.sort_values("Leakage_Rate", ascending=False)

fig_dept = px.bar(
dept_summary,
x="Department",
y="Leakage_Rate",
color="Department",
color_discrete_map=dept_colors
)

fig_dept.update_yaxes(title="Leakage Rate (%)")

st.plotly_chart(fig_dept, use_container_width=True)

st.subheader("Revenue Leakage Distribution")

fig3 = px.treemap(
dept_summary,
path=["Department"],
values="Leakage",
color="Department",
color_discrete_map=dept_colors
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("Billing vs Approved Claims")

sample_df = filtered_df.sample(min(len(filtered_df), 5000))

fig5 = px.scatter(
sample_df,
x="Billing_Amount",
y="Approved_Amount",
color="Denial_Flag",
size="Billing_Amount",
opacity=0.6
)

fig5.update_xaxes(tickformat=",")
fig5.update_yaxes(tickformat=",")

st.plotly_chart(fig5, use_container_width=True)

with st.expander("View Detailed Claim Data"):
    st.dataframe(filtered_df.head(10))