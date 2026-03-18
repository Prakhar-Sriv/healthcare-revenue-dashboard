import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("data/hospital_claims_60k_realistic_v2.csv")

df = df.drop_duplicates()

categorical_cols = [
    "Department",
    "Procedure_Code",
    "Insurance_Type"
]

for col in categorical_cols:
    df[col] = df[col].fillna("Unknown")

numerical_cols = [
    "Claim_Amount",
    "Billing_Amount",
    "Approved_Amount",
    "Expected_Revenue",
    "Actual_Revenue",
    "Payment_Received",
    "Documentation_Delay_Days",
    "Length_of_Stay",
    "Previous_Denial_Count"
]

for col in numerical_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(df[col].median())

df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")
df["Settlement_Date"] = pd.to_datetime(df["Settlement_Date"], errors="coerce")

df["Claim_Submission_Date"] = df["Claim_Submission_Date"].ffill()
df["Settlement_Date"] = df["Settlement_Date"].ffill()

df["Revenue_Leakage"] = df["Expected_Revenue"] - df["Actual_Revenue"]

df["Revenue_Leakage_Index"] = (
    df["Revenue_Leakage"] /
    df["Expected_Revenue"].replace(0, np.nan)
) * 100

df["Charge_Capture_Efficiency"] = (
    df["Billing_Amount"] /
    df["Expected_Revenue"].replace(0, np.nan)
) * 100

df["Accounts_Receivable_Days"] = (
    df["Settlement_Date"] - df["Claim_Submission_Date"]
).dt.days

df["Accounts_Receivable_Days"] = df["Accounts_Receivable_Days"].clip(lower=0)

df["Revenue_at_Risk"] = df["Billing_Amount"] - df["Payment_Received"]

df["Claim_Approval_Gap"] = df["Billing_Amount"] - df["Approved_Amount"]

df["Claim_Approval_Rate"] = (
    df["Approved_Amount"] /
    df["Billing_Amount"].replace(0, np.nan)
) * 100

for col in categorical_cols:
    encoder = LabelEncoder()
    df[col] = encoder.fit_transform(df[col])

df["Month"] = df["Claim_Submission_Date"].dt.to_period("M").astype(str)
df["Day_of_Week"] = df["Claim_Submission_Date"].dt.day_name()

df.to_csv("data/feature_store.csv", index=False)

print("Data preprocessing completed")
print(df.head())