import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PIL import Image

def show_dashboard():
    st.set_page_config(page_title="Medilytics Executive Dashboard", layout="wide")

    # ---------------------------
    # LOAD DATA
    # ---------------------------

    data = pd.read_csv(r"C:\Users\Prakhar\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Python 3.12\Medlytics\data\cleaned_claim_dataset.csv")
    data["Claim_Submission_Date"] = pd.to_datetime(data["Claim_Submission_Date"], format="%d-%m-%Y")

    # ---------------------------
    # SIDEBAR
    # ---------------------------

    with st.sidebar:

        logo = Image.open(r"C:\Users\Prakhar\Desktop\Prakhar\Cr_logo.png")
        st.image(logo, width=100)

        st.markdown("## Medilytics")
        st.markdown("Healthcare Revenue Intelligence")

        st.divider()

        st.markdown("### User Profile")
        st.write("Welcome!", st.session_state.username)
        st.write("Role:", st.session_state.role)

        st.divider()

        st.markdown("### Filters")

        # Date filter
        date_range = st.date_input(
            "Select Date Range",
            [data["Claim_Submission_Date"].min(),
            data["Claim_Submission_Date"].max()]
        )

        # Department filter
        department_filter = st.selectbox(
            "Department",
            ["All"] + list(data["Department"].unique())
        )

        # Insurance filter
        insurance_filter = st.selectbox(
            "Insurance Provider",
            ["All"] + list(data["Insurance_Type"].unique())
        )

        if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.role = None
                st.session_state.username = None
                st.rerun()

    # ---------------------------
    # APPLY FILTERS
    # ---------------------------

    filtered_data = data.copy()

    if len(date_range) == 2:
        filtered_data = filtered_data[
            (filtered_data["Claim_Submission_Date"] >= pd.to_datetime(date_range[0])) &
            (filtered_data["Claim_Submission_Date"] <= pd.to_datetime(date_range[1]))
        ]

    if department_filter != "All":
        filtered_data = filtered_data[
            filtered_data["Department"] == department_filter
        ]

    if insurance_filter != "All":
        filtered_data = filtered_data[
            filtered_data["Insurance_Type"] == insurance_filter
        ]

    # ---------------------------
    # KPI CALCULATIONS
    # ---------------------------

    total_revenue = filtered_data["Actual_Revenue"].sum()

    net_revenue = filtered_data["Payment_Received"].sum()

    avg_revenue = filtered_data["Actual_Revenue"].mean()

    approval_rate = (
        (filtered_data["Denial_Flag"] == 0).sum() /
        len(filtered_data)
    ) * 100

    revenue_leakage = (
        filtered_data["Expected_Revenue"].sum() -
        filtered_data["Actual_Revenue"].sum()
    )

    # ---------------------------
    # KPI CARDS
    # ---------------------------

    st.title("Executive Overview")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col2.metric("Net Revenue", f"₹{net_revenue:,.0f}")
    col3.metric("Avg Revenue per Patient", f"₹{avg_revenue:,.0f}")
    col4.metric("Claim Approval Rate", f"{approval_rate:.2f}%")
    col5.metric("Revenue Leakage", f"₹{revenue_leakage:,.0f}")

    st.divider()

    # ---------------------------
    # CHARTS IN COLUMNS
    # ---------------------------

    chart1, chart2 = st.columns(2)

    # ---------------------------
    # MONTHLY REVENUE TREND
    # ---------------------------

    monthly_revenue = (
        filtered_data
        .groupby(filtered_data["Claim_Submission_Date"].dt.to_period("M"))["Actual_Revenue"]
        .sum()
    )

    monthly_revenue.index = monthly_revenue.index.astype(str)

    fig1, ax1 = plt.subplots()

    ax1.plot(monthly_revenue.index, monthly_revenue.values, marker='o')

    ax1.set_title("Monthly Revenue Trend")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Revenue (₹ Lakhs)")
    ax1.tick_params(axis='x', rotation=45)

    # Convert numbers to Lakhs
    ax1.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'{x/100000:.1f} L')
    )

    chart1.pyplot(fig1)


    # ---------------------------
    # DEPARTMENT REVENUE CHART
    # ---------------------------

    dept_revenue = (
        filtered_data
        .groupby("Department")["Actual_Revenue"]
        .sum()
    )

    fig2, ax2 = plt.subplots()

    dept_revenue.plot(kind="bar", ax=ax2)

    ax2.set_title("Department-wise Revenue")
    ax2.set_xlabel("Department")
    ax2.set_ylabel("Revenue (₹ Lakhs)")
    ax2.tick_params(axis='x', rotation=45)

    ax2.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f'{x/100000:.1f} L')
    )

    chart2.pyplot(fig2)


    # ---------------------------
    # TABLES SECTION
    # ---------------------------

    colA, colB = st.columns(2)

    # Top departments
    top_departments = (
        filtered_data
        .groupby("Department")["Actual_Revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    colA.subheader("Top Revenue Generating Departments")
    colA.dataframe(top_departments.head(10), use_container_width=True)

    # Outstanding claims
    outstanding_claims = filtered_data[
        filtered_data["Payment_Received"] < filtered_data["Actual_Revenue"]
    ]

    colB.subheader("Outstanding Claims")

    colB.dataframe(
        outstanding_claims[
            ["Claim_ID", "Department", "Actual_Revenue", "Payment_Received"]
        ].head(10),
        use_container_width=True
    )
