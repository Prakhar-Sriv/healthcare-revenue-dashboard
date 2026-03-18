import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# ---------------------------------------------------------
# Load Feature Store
# ---------------------------------------------------------

df = pd.read_csv("data/feature_store.csv")

features = [
    "Department",
    "Procedure_Code",
    "Insurance_Type",
    "Claim_Amount",
    "Documentation_Delay_Days",
    "Length_of_Stay",
    "Previous_Denial_Count"
]

target = "Denial_Flag"

X = df[features].copy()
y = df[target]

# ---------------------------------------------------------
# Handle Missing Values
# ---------------------------------------------------------

X = X.fillna(X.median(numeric_only=True))

# ---------------------------------------------------------
# Encode Categorical Variables
# ---------------------------------------------------------

X = pd.get_dummies(
    X,
    columns=["Department", "Procedure_Code", "Insurance_Type"],
    drop_first=True
)

# ---------------------------------------------------------
# Feature Scaling
# ---------------------------------------------------------

numeric_features = [
    "Claim_Amount",
    "Documentation_Delay_Days",
    "Length_of_Stay",
    "Previous_Denial_Count"
]

scaler = StandardScaler()
X[numeric_features] = scaler.fit_transform(X[numeric_features])

# ---------------------------------------------------------
# Train Test Split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ---------------------------------------------------------
# Train Logistic Regression Model
# ---------------------------------------------------------

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# ---------------------------------------------------------
# Model Evaluation
# ---------------------------------------------------------

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_prob)

print("\nModel Evaluation")
print("Accuracy:", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1 Score:", round(f1, 4))
print("ROC-AUC:", round(roc_auc, 4))

# ---------------------------------------------------------
# Predict Denial Probability for Entire Dataset
# ---------------------------------------------------------

df_encoded = pd.get_dummies(
    df[features],
    columns=["Department", "Procedure_Code", "Insurance_Type"],
    drop_first=True
)

df_encoded = df_encoded.fillna(df_encoded.median(numeric_only=True))

# IMPORTANT: Match training columns
df_encoded = df_encoded.reindex(columns=X.columns, fill_value=0)

df_encoded[numeric_features] = scaler.transform(df_encoded[numeric_features])

df["Denial_Probability"] = model.predict_proba(df_encoded)[:, 1]

# ---------------------------------------------------------
# Risk Level Classification
# ---------------------------------------------------------

def risk_level(p):
    if p < 0.3:
        return "Low"
    elif p < 0.7:
        return "Medium"
    else:
        return "High"

df["Risk_Level"] = df["Denial_Probability"].apply(risk_level)

# ---------------------------------------------------------
# Risk Score (0–100)
# ---------------------------------------------------------

df["Denial_Risk_Score"] = (df["Denial_Probability"] * 100).round(2)

# ---------------------------------------------------------
# Prediction Confidence
# ---------------------------------------------------------

def confidence(p):
    if p > 0.85 or p < 0.15:
        return "High Confidence"
    elif p > 0.7 or p < 0.3:
        return "Moderate Confidence"
    else:
        return "Low Confidence"

df["Prediction_Confidence"] = df["Denial_Probability"].apply(confidence)

# ---------------------------------------------------------
# Save Predictions
# ---------------------------------------------------------

predictions = df[[
    "Claim_ID",
    "Denial_Probability",
    "Denial_Risk_Score",
    "Risk_Level",
    "Prediction_Confidence"
]]

predictions.to_csv(
    "data/denial_model_predictions.csv",
    index=False
)

# ---------------------------------------------------------
# Save Model Metrics
# ---------------------------------------------------------

metrics = pd.DataFrame({
    "Accuracy": [accuracy],
    "Precision": [precision],
    "Recall": [recall],
    "F1_Score": [f1],
    "ROC_AUC": [roc_auc]
})

metrics.to_csv(
    "data/denial_model_metrics.csv",
    index=False
)

# ---------------------------------------------------------
# Save Feature Importance
# ---------------------------------------------------------

importance = pd.DataFrame({
    "Feature": X.columns,
    "Coefficient": model.coef_[0]
})

importance = importance.sort_values(
    by="Coefficient",
    key=abs,
    ascending=False
)

importance.to_csv(
    "data/denial_feature_importance.csv",
    index=False
)

# ---------------------------------------------------------
# Save Model and Scaler
# ---------------------------------------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/denial_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("\nDenial prediction model completed successfully")