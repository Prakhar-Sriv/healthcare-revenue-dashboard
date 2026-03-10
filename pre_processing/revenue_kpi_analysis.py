import pandas as pd

df = pd.read_csv("cleaned_claim_dataset.csv")

df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"])
df["Settlement_Date"] = pd.to_datetime(df["Settlement_Date"])

df["Revenue_Leakage"] = df["Expected_Revenue"] - df["Actual_Revenue"]

df["Revenue_Leakage_Index"] = (df["Revenue_Leakage"] / df["Expected_Revenue"]) * 100

df["Charge_Capture_Efficiency"] = (df["Billing_Amount"] / df["Expected_Revenue"]) * 100

df["Accounts_Receivable_Days"] = (
    df["Settlement_Date"] - df["Claim_Submission_Date"]
).dt.days

df["Revenue_at_Risk"] = df["Billing_Amount"] - df["Payment_Received"]

department_profitability = df.groupby("Department").agg({
    "Expected_Revenue": "sum",
    "Actual_Revenue": "sum",
    "Revenue_Leakage": "sum",
    "Revenue_at_Risk": "sum"
}).reset_index()

department_profitability["Department_Profitability"] = (
    department_profitability["Actual_Revenue"] /
    department_profitability["Expected_Revenue"]
) * 100

kpi_summary = pd.DataFrame({
    "Total_Expected_Revenue":[df["Expected_Revenue"].sum()],
    "Total_Actual_Revenue":[df["Actual_Revenue"].sum()],
    "Total_Revenue_Leakage":[df["Revenue_Leakage"].sum()],
    "Average_Revenue_Leakage_Index":[df["Revenue_Leakage_Index"].mean()],
    "Average_Charge_Capture_Efficiency":[df["Charge_Capture_Efficiency"].mean()],
    "Average_Accounts_Receivable_Days":[df["Accounts_Receivable_Days"].mean()],
    "Total_Revenue_at_Risk":[df["Revenue_at_Risk"].sum()]
})

df.to_csv("claim_kpi_dataset.csv", index=False)
department_profitability.to_csv("department_profitability.csv", index=False)
kpi_summary.to_csv("hospital_kpi_summary.csv", index=False)
