from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from ml.model_utils import save_metadata, save_model
from ml.preprocessing import build_preprocessor, get_feature_columns

DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_security_logs.csv"


def prepare_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError("Dataset must contain a label column")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["login_hour"] = df["timestamp"].dt.hour.fillna(0)
    df["label"] = df["label"].str.lower().str.strip()
    df["label"] = df["label"].apply(lambda value: "suspicious" if value in {"suspicious", "high", "malicious"} else "normal")
    return df


def train_models() -> dict:
    df = prepare_dataset()
    feature_columns = get_feature_columns()
    X = df[feature_columns].copy()
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocessor = build_preprocessor(X_train)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    rf_model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    rf_model.fit(X_train_processed, y_train)

    y_pred = rf_model.predict(X_test_processed)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label="suspicious", zero_division=0)
    recall = recall_score(y_test, y_pred, pos_label="suspicious", zero_division=0)
    f1 = f1_score(y_test, y_pred, pos_label="suspicious", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=["normal", "suspicious"])

    iso_model = IsolationForest(contamination=0.2, random_state=42)
    iso_model.fit(X_train_processed)

    model_dir = Path(__file__).resolve().parents[1] / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    save_model(preprocessor, "preprocessor.pkl")
    save_model(rf_model, "random_forest.pkl")
    save_model(iso_model, "isolation_forest.pkl")

    metadata = {
        "model_name": "CyberSentinel Random Forest",
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "dataset_size": len(df),
        "class_distribution": {k: int(v) for k, v in dict(df["label"].value_counts()).items()},
        "confusion_matrix": cm.tolist(),
        "class_report": classification_report(y_test, y_pred, output_dict=True),
    }
    save_metadata(metadata)

    return metadata


if __name__ == "__main__":
    result = train_models()
    print(json.dumps(result, indent=2))
