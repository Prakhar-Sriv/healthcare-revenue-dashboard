import pandas as pd
import numpy as np


def preprocess(df):

    df["Settlement_Date"] = pd.to_datetime(df["Settlement_Date"], errors="coerce")
    df["Claim_Submission_Date"] = pd.to_datetime(df["Claim_Submission_Date"], errors="coerce")

    numeric_cols = [
        "Expected_Revenue","Actual_Revenue","Billing_Amount",
        "Claim_Amount","Approved_Amount","Payment_Received"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Outstanding_Revenue"] = df["Claim_Amount"] - df["Payment_Received"]

    df["Revenue_Realization_Rate"] = (
        df["Actual_Revenue"] /
        df["Expected_Revenue"].replace(0, np.nan)
    ) * 100

    df["Collection_Efficiency"] = (
        df["Payment_Received"] /
        df["Billing_Amount"].replace(0, np.nan)
    ) * 100

    df["Claim_Processing_Time"] = (
        df["Settlement_Date"] - df["Claim_Submission_Date"]
    ).dt.days

    df["Underpayment_Rate"] = (
        (df["Claim_Amount"] - df["Approved_Amount"]) /
        df["Claim_Amount"].replace(0, np.nan)
    ) * 100

    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    return df


# ---------------- ADMIN METRICS ---------------- #

def get_admin_metrics(df):

    df = preprocess(df)

    total_revenue = df["Billing_Amount"].sum()
    approved_revenue = df["Approved_Amount"].sum()
    total_claims = len(df)

    approved_claims = (df["Denial_Flag"] == 0).sum()
    approval_rate = (approved_claims / total_claims) * 100 if total_claims else 0
    denial_rate = 100 - approval_rate

    leakage = total_revenue - approved_revenue

    return {
        "total_revenue": total_revenue,
        "approval_rate": approval_rate,
        "denial_rate": denial_rate,
        "revenue_leakage": leakage
    }


# ---------------- FINANCE METRICS ---------------- #

def get_finance_metrics(df):

    df = preprocess(df)

    return {
        "collection_efficiency": df["Collection_Efficiency"].mean(),
        "outstanding_revenue": df["Outstanding_Revenue"].sum(),
        "underpayment_rate": df["Underpayment_Rate"].mean(),
        "revenue_realization": df["Revenue_Realization_Rate"].mean()
    }


# ---------------- DOCTOR METRICS ---------------- #

def get_doctor_metrics(df):

    df = preprocess(df)

    total_patients = df["Patient_ID"].nunique()

    net_revenue_per_patient = (
        df["Payment_Received"].sum() / total_patients
        if total_patients else 0
    )

    return {
        "avg_length_of_stay": df["Length_of_Stay"].mean(),
        "avg_claim_processing_time": df["Claim_Processing_Time"].mean(),
        "net_revenue_per_patient": net_revenue_per_patient
    }


# ---------------- ANALYST METRICS ---------------- #

def get_analyst_metrics(df):

    df = preprocess(df)

    total_claims = len(df)
    total_denied = df["Denial_Flag"].sum()

    denial_rate = (total_denied / total_claims) * 100 if total_claims else 0

    return {
        "total_claims": total_claims,
        "denial_rate": denial_rate,
        "avg_processing_time": df["Claim_Processing_Time"].mean()
    }