import pandas as pd
import os
import joblib
from sklearn.ensemble import IsolationForest

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

X = X.fillna(X.median(numeric_only=True))

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

model.fit(X)

df["Anomaly_Flag"] = model.predict(X)

df["Anomaly_Flag"] = df["Anomaly_Flag"].map({1:0,-1:1})

df["Anomaly_Score"] = model.decision_function(X)

total_anomalies = df["Anomaly_Flag"].sum()
anomaly_percentage = (total_anomalies / len(df)) * 100

anomaly_claim_revenue = df[df["Anomaly_Flag"]==1]["Claim_Amount"].sum()
anomaly_expected_revenue = df[df["Anomaly_Flag"]==1]["Expected_Revenue"].sum()

print("\nAnomaly Detection Completed")
print("Total Anomalies:", total_anomalies)
print("Anomaly Percentage:", round(anomaly_percentage,2),"%")
print("Claim Revenue Impact:", anomaly_claim_revenue)
print("Expected Revenue Exposure:", anomaly_expected_revenue)

output = df[[
    "Claim_ID",
    "Anomaly_Flag",
    "Anomaly_Score"
]]

output.to_csv("data/anomaly_flags.csv", index=False)

os.makedirs("models", exist_ok=True)

joblib.dump(model,"models/anomaly_model.pkl")

print("\nAnomaly model saved successfully")