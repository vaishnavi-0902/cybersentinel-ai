from pathlib import Path

import pandas as pd


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_security_logs.csv"


def test_dataset_exists_and_has_required_columns():
    assert DATASET_PATH.exists(), "Sample dataset should exist at data/sample_security_logs.csv"
    df = pd.read_csv(DATASET_PATH)
    required = {
        "timestamp",
        "user_id",
        "source_ip",
        "destination_ip",
        "login_attempts",
        "failed_logins",
        "request_count",
        "session_duration",
        "bytes_sent",
        "bytes_received",
        "login_hour",
        "country",
        "device_type",
        "protocol",
        "port_category",
        "authentication_status",
        "previous_activity",
        "label",
    }
    missing = required - set(df.columns)
    assert not missing, f"Missing required columns: {sorted(missing)}"
    assert len(df) > 0
