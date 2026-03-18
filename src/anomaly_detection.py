import pandas as pd
import os
import joblib
from sklearn.ensemble import IsolationForest

# ---------------------------------------------------------
# Load Feature Store
# ---------------------------------------------------------

df = pd.read_csv("data/feature_store.csv")

features = [
    "Claim_Amount",
    "Billing_Amount",
    "Approved_Amount",
    "Length_of_Stay",
    "Documentation_Delay_Days",
    "Expected_Revenue"
]

X = df[features].copy()

# ---------------------------------------------------------
# Handle Missing Values
# ---------------------------------------------------------

X = X.fillna(X.median(numeric_only=True))

# ---------------------------------------------------------
# Train Isolation Forest
# ---------------------------------------------------------

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

model.fit(X)

# ---------------------------------------------------------
# Generate Anomaly Predictions
# ---------------------------------------------------------

df["Anomaly_Flag"] = model.predict(X)

# Convert: normal=0, anomaly=1
df["Anomaly_Flag"] = df["Anomaly_Flag"].map({1:0, -1:1})

# Raw anomaly score
df["Anomaly_Score"] = model.decision_function(X)

# ---------------------------------------------------------
# Anomaly Severity Classification
# ---------------------------------------------------------

def severity(score):
    if score < -0.20:
        return "Critical"
    elif score < -0.10:
        return "High"
    elif score < -0.05:
        return "Moderate"
    else:
        return "Low"

df["Anomaly_Severity"] = df["Anomaly_Score"].apply(severity)

# ---------------------------------------------------------
# Summary Metrics
# ---------------------------------------------------------

total_anomalies = df["Anomaly_Flag"].sum()
anomaly_percentage = (total_anomalies / len(df)) * 100

anomaly_claim_revenue = df[df["Anomaly_Flag"] == 1]["Claim_Amount"].sum()
anomaly_expected_revenue = df[df["Anomaly_Flag"] == 1]["Expected_Revenue"].sum()

print("\nAnomaly Detection Completed")
print("Total Anomalies:", total_anomalies)
print("Anomaly Percentage:", round(anomaly_percentage, 2), "%")
print("Claim Revenue Impact:", round(anomaly_claim_revenue, 2))
print("Expected Revenue Exposure:", round(anomaly_expected_revenue, 2))

# ---------------------------------------------------------
# Save Anomaly Flags (Dashboard Table)
# ---------------------------------------------------------

anomaly_output = df[[
    "Claim_ID",
    "Anomaly_Flag",
    "Anomaly_Score",
    "Anomaly_Severity"
]]

anomaly_output = anomaly_output.sort_values(
    by="Anomaly_Score"
)

anomaly_output.to_csv(
    "data/anomaly_flags.csv",
    index=False
)

# ---------------------------------------------------------
# Save Summary Metrics for Dashboard KPIs
# ---------------------------------------------------------

summary = pd.DataFrame({
    "Total_Claims":[len(df)],
    "Total_Anomalies":[total_anomalies],
    "Anomaly_Percentage":[round(anomaly_percentage,2)],
    "Anomalous_Claim_Revenue":[anomaly_claim_revenue],
    "Expected_Revenue_Exposure":[anomaly_expected_revenue]
})

summary.to_csv(
    "data/anomaly_summary_metrics.csv",
    index=False
)

# ---------------------------------------------------------
# Save Model
# ---------------------------------------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/anomaly_model.pkl"
)

print("\nAnomaly model saved successfully")