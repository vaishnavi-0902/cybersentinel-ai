from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

from backend.app.config import PROJECT_ROOT
from backend.app.security.rules import evaluate_security_rules

MODEL_DIR = PROJECT_ROOT / "models"


def _model_path(name: str) -> Path:
    return MODEL_DIR / name


def _load_model(name: str):
    path = _model_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


def load_metadata() -> Dict[str, Any]:
    metadata_path = MODEL_DIR / "metadata.json"
    if metadata_path.exists():
        with metadata_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def prepare_features(event: Dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame([event])
    feature_columns = [
        "failed_logins",
        "request_count",
        "session_duration",
        "bytes_sent",
        "bytes_received",
        "login_hour",
        "login_attempts",
        "previous_activity",
        "authentication_status",
        "device_type",
        "protocol",
        "port_category",
        "country",
    ]
    for column in feature_columns:
        if column not in df.columns:
            df[column] = 0 if column not in {"previous_activity", "authentication_status", "device_type", "protocol", "port_category", "country"} else "unknown"
    return df


def predict_event(event: Dict[str, Any]) -> Dict[str, Any]:
    rf_model = _load_model("random_forest.pkl")
    iso_model = _load_model("isolation_forest.pkl")
    preprocessor = _load_model("preprocessor.pkl")

    record = prepare_features(event)
    transformed = preprocessor.transform(record)

    model_prediction = rf_model.predict(transformed)[0]
    proba = rf_model.predict_proba(transformed)[0]
    anomaly_score = float(iso_model.score_samples(transformed)[0])
    anomaly_score_norm = max(0.0, min(1.0, abs(anomaly_score) / 10.0))
    risk_score = int(round(float(proba[1]) * 70 + anomaly_score_norm * 30))
    risk_score = max(0, min(100, risk_score))

    reasons = evaluate_security_rules(event)
    if not reasons:
        reasons = ["No major rule violations detected"]

    if model_prediction == "suspicious" or risk_score >= 60:
        severity = "critical" if risk_score >= 80 else "high" if risk_score >= 60 else "medium"
        prediction = "suspicious"
    else:
        severity = "low" if risk_score < 30 else "medium"
        prediction = "normal"

    if risk_score >= 80:
        severity = "critical"

    return {
        "prediction": prediction,
        "risk_score": risk_score,
        "severity": severity,
        "anomaly_score": round(float(anomaly_score_norm), 3),
        "reasons": reasons,
    }


def batch_predict(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [predict_event(event) for event in events]
