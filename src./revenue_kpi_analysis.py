import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

os.makedirs(DATA_DIR, exist_ok=True)

feature_store_path = os.path.join(DATA_DIR, "feature_store.csv")

df = pd.read_csv(feature_store_path)

df["Expected_Revenue"] = pd.to_numeric(df["Expected_Revenue"], errors="coerce").fillna(0)
df["Actual_Revenue"] = pd.to_numeric(df["Actual_Revenue"], errors="coerce").fillna(0)
df["Billing_Amount"] = pd.to_numeric(df["Billing_Amount"], errors="coerce").fillna(0)
df["Payment_Received"] = pd.to_numeric(df["Payment_Received"], errors="coerce").fillna(0)

# Revenue Leakage → difference between expected hospital revenue and actual revenue generated
df["Revenue_Leakage"] = df["Expected_Revenue"] - df["Actual_Revenue"]

# Revenue Leakage Index (%) → proportion of lost revenue compared to expected revenue
df["Revenue_Leakage_Index"] = (
    df["Revenue_Leakage"] /
    df["Expected_Revenue"].replace(0, np.nan)
) * 100

# Charge Capture Efficiency → efficiency of converting expected revenue into billed charges
df["Charge_Capture_Efficiency"] = (
    df["Billing_Amount"] /
    df["Expected_Revenue"].replace(0, np.nan)
) * 100

# Revenue at Risk → billed revenue that is still pending collection
df["Revenue_at_Risk"] = df["Billing_Amount"] - df["Payment_Received"]

department_profitability = df.groupby("Department").agg({
    "Expected_Revenue": "sum",
    "Actual_Revenue": "sum",
    "Revenue_Leakage": "sum",
    "Revenue_at_Risk": "sum"
}).reset_index()

# Department Profitability (%) → percentage of expected revenue actually realized
department_profitability["Department_Profitability"] = (
    department_profitability["Actual_Revenue"] /
    department_profitability["Expected_Revenue"].replace(0, np.nan)
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

kpi_display = kpi_summary.copy()

for col in [
    "Total_Expected_Revenue",
    "Total_Actual_Revenue",
    "Total_Revenue_Leakage",
    "Total_Revenue_at_Risk"
]:
    kpi_display[col] = kpi_display[col].apply(indian_format)

df.to_csv(os.path.join(DATA_DIR,"claim_kpi_dataset.csv"), index=False)
department_profitability.to_csv(os.path.join(DATA_DIR,"department_profitability.csv"), index=False)

kpi_display.to_csv(os.path.join(DATA_DIR,"hospital_kpi_summary.csv"), index=False)

print("\nRevenue KPI analysis completed\n")
print(kpi_display)