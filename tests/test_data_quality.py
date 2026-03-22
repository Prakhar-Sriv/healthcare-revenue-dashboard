import os
import pandas as pd
import pytest

# Path to data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

@pytest.fixture
def anomaly_flags():
    return pd.read_csv(os.path.join(DATA_DIR, "anomaly_flags.csv"))

@pytest.fixture
def feature_store():
    return pd.read_csv(os.path.join(DATA_DIR, "feature_store.csv"))

@pytest.fixture
def hospital_claims():
    return pd.read_csv(os.path.join(DATA_DIR, "hospital_claims_60k_realistic_v2.csv"))

# ---------- Data Quality Tests ----------

def test_unique_claim_ids(feature_store, hospital_claims):
    """Claim_ID should be unique within each dataset."""
    assert feature_store["Claim_ID"].is_unique, "Duplicate Claim_IDs in feature_store"
    assert hospital_claims["Claim_ID"].is_unique, "Duplicate Claim_IDs in hospital_claims"

def test_claim_id_consistency(feature_store, hospital_claims):
    """Claim_IDs in feature_store should exist in hospital_claims."""
    missing_ids = set(feature_store["Claim_ID"]) - set(hospital_claims["Claim_ID"])
    assert not missing_ids, f"Claim_IDs missing in hospital_claims: {missing_ids}"

def test_anomaly_flags_link(anomaly_flags, hospital_claims):
    """Every Claim_ID in anomaly_flags should exist in hospital_claims."""
    missing_ids = set(anomaly_flags["Claim_ID"]) - set(hospital_claims["Claim_ID"])
    assert not missing_ids, f"Claim_IDs missing in hospital_claims: {missing_ids}"

def test_revenue_consistency(feature_store):
    """Expected_Revenue should be >= Actual_Revenue."""
    invalid_rows = feature_store[feature_store["Expected_Revenue"] < feature_store["Actual_Revenue"]]
    assert invalid_rows.empty, f"Rows with Expected_Revenue < Actual_Revenue: {invalid_rows['Claim_ID'].tolist()}"

# def test_payment_consistency(feature_store):
#     """Payment_Received should never exceed Approved_Amount."""
#     invalid_rows = feature_store[feature_store["Payment_Received"] > feature_store["Approved_Amount"]]
#     assert invalid_rows.empty, f"Rows with Payment_Received > Approved_Amount: {invalid_rows['Claim_ID'].tolist()}"

def test_date_consistency(feature_store):
    """Admission_Date should be before Discharge_Date."""
    invalid_rows = feature_store[pd.to_datetime(feature_store["Admission_Date"]) > pd.to_datetime(feature_store["Discharge_Date"])]
    assert invalid_rows.empty, f"Invalid admission/discharge dates in Claim_IDs: {invalid_rows['Claim_ID'].tolist()}"

def test_length_of_stay(feature_store):
    """Length_of_Stay should equal (Discharge_Date - Admission_Date)."""
    feature_store["Admission_Date"] = pd.to_datetime(feature_store["Admission_Date"])
    feature_store["Discharge_Date"] = pd.to_datetime(feature_store["Discharge_Date"])
    calculated_stay = (feature_store["Discharge_Date"] - feature_store["Admission_Date"]).dt.days
    mismatched = feature_store[feature_store["Length_of_Stay"] != calculated_stay]
    assert mismatched.empty, f"Mismatched Length_of_Stay for Claim_IDs: {mismatched['Claim_ID'].tolist()}"


