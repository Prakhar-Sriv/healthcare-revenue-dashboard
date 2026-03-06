import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("synthetic_hospital_revenue_data_70k_raw.csv")

df = df.drop_duplicates()

categorical_cols = ["Department","Procedure_Code","Insurance_Type"]
for col in categorical_cols:
    df[col] = df[col].fillna("Unknown")

numerical_cols = [
"Expected_Revenue","Actual_Revenue","Billing_Amount","Payment_Received",
"Claim_Amount","Approved_amount","Documentation_Delay_Days",
"Length_of_Stay","Previous_Denial_Count","Denial_Flag"
]

for col in numerical_cols:
    df[col] = df[col].fillna(df[col].median())

money_cols = [
"Expected_Revenue","Actual_Revenue","Billing_Amount",
"Payment_Received","Claim_Amount","Approved_amount"
]

for col in money_cols:
    df[col] = df[col].apply(lambda x: abs(x))

df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")
df["Settlement_Date"] = pd.to_datetime(df["Settlement_Date"], errors="coerce")

df["Settlement_Days"] = (df["Settlement_Date"] - df["Claim_Submission_Date"]).dt.days
df["Accounts_Receivable_Days"] = df["Settlement_Days"]

df["Revenue_Leakage"] = df["Expected_Revenue"] - df["Actual_Revenue"]
df["Revenue_Leakage_Index"] = (df["Revenue_Leakage"] / df["Expected_Revenue"]) * 100
df["Charge_Capture_Efficiency"] = (df["Billing_Amount"] / df["Expected_Revenue"]) * 100
df["Revenue_at_Risk"] = df["Billing_Amount"] - df["Payment_Received"]

encoder = LabelEncoder()
for col in categorical_cols:
    df[col] = encoder.fit_transform(df[col])

df["Month"] = df["Claim_Submission_Date"].dt.to_period("M").astype(str)

df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()

for col in money_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df = df[(df[col] >= lower) & (df[col] <= upper)]

monthly_df = df.groupby("Month").agg({
"Actual_Revenue":"sum",
"Expected_Revenue":"sum",
"Claim_ID":"count",
"Denial_Flag":"sum"
}).reset_index()

monthly_df.columns = [
"Month",
"Total_Actual_Revenue",
"Total_Expected_Revenue",
"Total_Claims",
"Total_Denied_Claims"
]

monthly_df["Outstanding_Amount"] = monthly_df["Total_Expected_Revenue"] - monthly_df["Total_Actual_Revenue"]

df.to_csv("cleaned_claim_dataset.csv", index=False)
monthly_df.to_csv("monthly_revenue_dataset.csv", index=False)