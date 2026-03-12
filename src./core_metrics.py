import pandas as pd
import numpy as np
import os

df = pd.read_csv("data/feature_store.csv")

df["Settlement_Date"] = pd.to_datetime(df["Settlement_Date"], errors="coerce")
df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")

total_claims = df["Claim_ID"].nunique()
total_patients = df["Patient_ID"].nunique()

# Outstanding Revenue → amount yet to be collected after billing
df["Outstanding_Revenue"] = df["Claim_Amount"].fillna(0) - df["Payment_Received"].fillna(0)

total_denied_claims = df["Denial_Flag"].fillna(0).sum()

# Denial Rate (%) → percentage of claims rejected by insurers
denial_rate = (total_denied_claims / total_claims) * 100 if total_claims > 0 else 0

# Revenue Realization Rate → proportion of expected revenue actually earned
df["Revenue_Realization_Rate"] = (
    df["Actual_Revenue"].fillna(0) /
    df["Expected_Revenue"].replace(0, np.nan)
) * 100

# Collection Efficiency → efficiency of converting billed revenue into collected payments
df["Collection_Efficiency"] = (
    df["Payment_Received"].fillna(0) /
    df["Billing_Amount"].replace(0, np.nan)
) * 100

# Claim Processing Time → time taken for claim settlement
df["Claim_Processing_Time"] = (
    df["Settlement_Date"] -
    df["Claim_Submission_Date"]
).dt.days

# Underpayment Rate → portion of claim amount not approved by insurers
df["Underpayment_Rate"] = (
    (df["Claim_Amount"].fillna(0) - df["Approved_Amount"].fillna(0)) /
    df["Claim_Amount"].replace(0, np.nan)
) * 100

net_revenue_per_patient = (
    df["Payment_Received"].fillna(0).sum() / total_patients
) if total_patients > 0 else 0

core_metrics = pd.DataFrame({
    "Total_Patients":[total_patients],
    "Total_Claims":[total_claims],
    "Total_Denied_Claims":[total_denied_claims],
    "Denial_Rate":[denial_rate],
    "Average_Revenue_Realization_Rate":[df["Revenue_Realization_Rate"].mean()],
    "Average_Collection_Efficiency":[df["Collection_Efficiency"].mean()],
    "Average_Claim_Processing_Time":[df["Claim_Processing_Time"].mean()],
    "Average_Underpayment_Rate":[df["Underpayment_Rate"].mean()],
    "Net_Revenue_per_Patient":[net_revenue_per_patient],
    "Total_Outstanding_Revenue":[df["Outstanding_Revenue"].sum()]
})

def indian_format(num):
    num = int(round(num))
    s = str(num)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last3

display_metrics = core_metrics.copy()

display_metrics["Net_Revenue_per_Patient"] = display_metrics["Net_Revenue_per_Patient"].apply(indian_format)
display_metrics["Total_Outstanding_Revenue"] = display_metrics["Total_Outstanding_Revenue"].apply(indian_format)

os.makedirs("data", exist_ok=True)

display_metrics.to_csv("data/core_hospital_metrics.csv", index=False)

print("\nCore hospital metrics generated\n")
print(display_metrics)