from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from ml.train import prepare_dataset

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def evaluate_models() -> dict:
    df = prepare_dataset()
    metadata = json.loads((MODEL_DIR / "metadata.json").read_text(encoding="utf-8"))
    return metadata


if __name__ == "__main__":
    print(json.dumps(evaluate_models(), indent=2))
