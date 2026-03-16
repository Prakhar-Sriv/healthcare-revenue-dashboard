import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Medilytics – Claim Denial Prediction",
    layout="wide"
)

# -------- LOAD CSS -------- #
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------- HELPER FUNCTION ---------------- #
def clean_chart(fig):

    fig.update_layout(

        height=360,
        autosize=False,

        plot_bgcolor="#334155",
        paper_bgcolor="#334155",

        font=dict(color="white", size=14),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="white"),
            title=dict(font=dict(color="white"))
        ),

        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="white"),
            title=dict(font=dict(color="white"))
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="white")
        ),

        margin=dict(l=40, r=40, t=40, b=110)

    )

    return fig

def clean_chart(fig):

    fig.update_layout(

        height=500,
        autosize=False,

        plot_bgcolor="#334155",
        paper_bgcolor="#334155",

        font=dict(color="white", size=14),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="white"),
            title=dict(font=dict(color="white"))
        ),

        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="white"),
            title=dict(font=dict(color="white"))
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="white")
        ),

        margin=dict(l=40, r=40, t=40, b=110)

    )

    return fig
# ---------------- DASHBOARD TITLE ---------------- #
st.markdown("""
<h1 style='text-align:center; font-weight:700;'>
<span style="color:#FFEA00;">Medilytics AI</span>
<span style="color:white;">– Claim Denial</span>
<span style="color:#FFEA00;">Risk</span>
<span style="color:white;">Prediction Dashboard</span>
</h1>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ---------------- #
predictions = pd.read_csv("denial_model_predictions.csv")
metrics = pd.read_csv("denial_model_metrics.csv")
data = pd.read_csv("pre_processed_data.csv")
feature_importance = pd.read_csv("denial_feature_importance.csv")

merged = data.merge(predictions, on="Claim_ID")
# Create high risk dataset early so sidebar can use it
high_risk_df = merged[merged["Risk_Level"] == "High"]

st.markdown("""
<style>
.section-gap {
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
# ---------------- SIDEBAR FILTER ---------------- #
st.sidebar.header("Filters")

risk_filter = st.sidebar.selectbox(
    "Select Risk Level",
    ["All", "Low", "Medium", "High"]
)

if risk_filter != "All":
    filtered_data = predictions[predictions["Risk_Level"] == risk_filter]
else:
    filtered_data = predictions

st.sidebar.markdown("---")
st.sidebar.header("Predict Claim Denial Risk")

claim_amount_input = st.sidebar.text_input(
    "Claim Amount (₹)",
    "50000"
)

# convert to numeric
try:
    claim_amount = float(claim_amount_input)
except:
    claim_amount = 0
department_input = st.sidebar.selectbox(
    "Department",
    merged["Department"].unique()
)

insurance_input = st.sidebar.selectbox(
    "Insurance Type",
    merged["Insurance_Type"].unique()
)

predict_button = st.sidebar.button("Predict Risk")

if predict_button:

    # simple rule based prediction for demo
    base_prob = merged["Denial_Probability"].mean()

    if claim_amount > merged["Claim_Amount"].mean():
        base_prob += 0.05

    if department_input in high_risk_df["Department"].values:
        base_prob += 0.05

    if insurance_input in high_risk_df["Insurance_Type"].values:
        base_prob += 0.05

    if base_prob < 0.3:
        risk = "Low"
        color = "green"
    elif base_prob < 0.6:
        risk = "Medium"
        color = "orange"
    else:
        risk = "High"
        color = "red"

    st.sidebar.markdown(
        f"### Predicted Risk: <span style='color:{color}'>{risk}</span>",
        unsafe_allow_html=True
    )

    st.sidebar.write(f"Denial Probability: **{base_prob:.2f}**")
# ---------------- KPI CALCULATIONS ---------------- #

high_risk_df = merged[merged["Risk_Level"] == "High"]

dept_risk_counts = high_risk_df["Department"].value_counts()
top_risk_dept = dept_risk_counts.idxmax()

insurance_risk_counts = high_risk_df["Insurance_Type"].value_counts()
top_risk_insurance = insurance_risk_counts.idxmax()

potential_revenue_loss = high_risk_df["Claim_Amount"].sum()
potential_revenue_loss_cr = potential_revenue_loss / 10000000

highest_risk_claim = high_risk_df["Claim_Amount"].max()
highest_risk_claim_k = highest_risk_claim / 1000

dept_avg_prob = merged.groupby("Department")["Denial_Probability"].mean()
best_dept = dept_avg_prob.idxmin()

# ---------------- KPI DISPLAY ---------------- #

st.subheader("Operational Risk Indicators")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-title">Denial Risk Concentration</div>
    <div class="metric-value">{top_risk_dept}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-title">Highest Risk Insurance</div>
    <div class="metric-value">{top_risk_insurance}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-title">Potential Revenue Loss</div>
    <div class="metric-value">₹{potential_revenue_loss_cr:,.2f} Cr</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-title">Highest Risk Claim Value</div>
    <div class="metric-value">₹{highest_risk_claim_k:,.2f} K</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-title">Best Performing Department</div>
    <div class="metric-value">{best_dept}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.section-gap {
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

# ---------------- CHARTS ---------------- #

col1, col2 = st.columns([1,1], gap="large")
with col1:
    st.subheader("Denial Risk by Insurance Type")
    insurance_risk = merged.groupby("Insurance_Type")["Denial_Probability"].mean().reset_index()
    fig1 = px.bar(
        insurance_risk,
        x="Insurance_Type",
        y="Denial_Probability",
        color="Denial_Probability",
        color_continuous_scale="Reds"
    )
    fig1 = clean_chart(fig1)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True,config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("Claims at Risk by Department")
    dept_risk = merged.groupby(["Department","Risk_Level"]).size().reset_index(name="Count")
    fig2 = px.bar(
        dept_risk,
        x="Department",
        y="Count",
        color="Risk_Level",
        barmode="stack",
        text="Count",
        color_discrete_map={
            "Low":"#2ECC71",
            "Medium":"#F1C40F",
            "High":"#E74C3C"
        }
    )
    fig2 = clean_chart(fig2)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True,config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

#Row 2 
col3, col4 = st.columns([1,1], gap="large")

with col3:
    st.subheader("Denial Risk Trend Over Time")
    merged["Claim_Date"] = pd.to_datetime(merged["Claim_Submission_Date"], dayfirst=True, errors="coerce")
    merged["Year_Month"] = merged["Claim_Date"].dt.to_period("M")

    trend_data_monthly = merged.groupby("Year_Month")["Denial_Probability"].mean().reset_index()
    trend_data_monthly["Year_Month"] = trend_data_monthly["Year_Month"].astype(str)

    fig_trend_month = px.line(
        trend_data_monthly,
        x="Year_Month",
        y="Denial_Probability",
        markers=True
    )
    fig_trend_month = clean_chart(fig_trend_month)
    st.plotly_chart(fig_trend_month, use_container_width=True)

with col4:
    st.subheader("Claim Risk Level Distribution")
    risk_counts = merged["Risk_Level"].value_counts().reset_index()
    risk_counts.columns = ["Risk_Level", "Count"]

    fig4 = px.pie(
        risk_counts,
        names="Risk_Level",
        values="Count",
        hole=0.6,
        color="Risk_Level",
        color_discrete_map={
            "Low": "#2ECC71",
            "Medium": "#F1C40F",
            "High": "#E74C3C"
        }
    )

    fig4 = clean_chart(fig4)
    st.plotly_chart(fig4, use_container_width=True)
   
# ---------------- TABLE ---------------- #

st.subheader("Risk Claims Requiring Review")

filtered_data["Denial_Probability"] = pd.to_numeric(
    filtered_data["Denial_Probability"],
    errors="coerce"
)

top_claims = filtered_data.sort_values(
    "Denial_Probability",
    ascending=False
).head(10)

display_table = top_claims[
    ["Claim_ID","Denial_Probability","Risk_Level"]
].rename(columns={"Denial_Probability":"Risk_Score"})

st.dataframe(display_table, use_container_width=True)