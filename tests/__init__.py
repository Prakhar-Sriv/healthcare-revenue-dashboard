import os
import pandas as pd
import pytest

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


# Uniqueness of Claim_ID across datasets.
# Consistency of Claim_ID between tables.
# Revenue logic (Expected ≥ Actual).
# Payment logic (Payment ≤ Approved).
# Date integrity (Admission before Discharge).
# Length of stay correctness (matches date difference).