import pandas as pd
import os
import joblib
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

feature_store_path = os.path.join(DATA_DIR, "feature_store.csv")

df = pd.read_csv(feature_store_path)

df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")

df = df.dropna(subset=["Claim_Submission_Date"])

df = df.sort_values("Claim_Submission_Date")

df["Actual_Revenue"] = pd.to_numeric(df["Actual_Revenue"], errors="coerce").fillna(0)

monthly_revenue = df.groupby(
    df["Claim_Submission_Date"].dt.to_period("M")
)["Actual_Revenue"].sum().reset_index()

monthly_revenue["Month"] = monthly_revenue["Claim_Submission_Date"].astype(str)

monthly_revenue = monthly_revenue[["Month", "Actual_Revenue"]]

monthly_revenue.to_csv(
    os.path.join(DATA_DIR, "monthly_revenue_history.csv"),
    index=False
)

revenue_series = monthly_revenue["Actual_Revenue"]

model = ARIMA(revenue_series, order=(1,1,1))

model_fit = model.fit()

forecast_steps = 6

forecast_obj = model_fit.get_forecast(steps=forecast_steps)

forecast = forecast_obj.predicted_mean

conf_int = forecast_obj.conf_int()

last_month = pd.Period(monthly_revenue["Month"].iloc[-1], freq="M")

future_months = pd.period_range(
    start=last_month + 1,
    periods=forecast_steps,
    freq="M"
).astype(str)

forecast_results = pd.DataFrame({
    "Month": future_months,
    "Forecasted_Revenue": forecast.values,
    "Lower_Bound": conf_int.iloc[:, 0].values,
    "Upper_Bound": conf_int.iloc[:, 1].values
})

last_actual_revenue = revenue_series.iloc[-1]

forecast_results["Forecast_Growth_%"] = (
    (forecast_results["Forecasted_Revenue"] - last_actual_revenue)
    / last_actual_revenue
) * 100

in_sample_pred = model_fit.predict(start=1, end=len(revenue_series) - 1)

actual = revenue_series.iloc[1:]

mape = mean_absolute_percentage_error(actual, in_sample_pred) * 100

metrics = pd.DataFrame({
    "MAPE": [mape]
})

metrics.to_csv(
    os.path.join(DATA_DIR, "forecast_model_metrics.csv"),
    index=False
)

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

forecast_display = forecast_results.copy()

forecast_display["Forecasted_Revenue"] = forecast_display["Forecasted_Revenue"].apply(indian_format)
forecast_display["Lower_Bound"] = forecast_display["Lower_Bound"].apply(indian_format)
forecast_display["Upper_Bound"] = forecast_display["Upper_Bound"].apply(indian_format)

forecast_display.to_csv(
    os.path.join(DATA_DIR, "revenue_forecast.csv"),
    index=False
)

joblib.dump(
    model_fit,
    os.path.join(MODEL_DIR, "revenue_forecast_model.pkl")
)

print("\nRevenue Forecast Generated\n")
print("Model MAPE:", round(mape, 2), "%")
print(forecast_display)