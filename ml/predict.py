from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def predict_single_record(record: Dict[str, Any]) -> Dict[str, Any]:
    preprocessor = joblib.load(MODEL_DIR / "preprocessor.pkl")
    model = joblib.load(MODEL_DIR / "random_forest.pkl")
    feature_df = pd.DataFrame([record])
    transformed = preprocessor.transform(feature_df)
    prediction = model.predict(transformed)[0]
    probability = model.predict_proba(transformed)[0].max()
    return {"prediction": prediction, "probability": float(probability)}
