from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def save_model(model: Any, name: str) -> None:
    MODEL_DIR.mkdir(exist_ok=True, parents=True)
    joblib.dump(model, MODEL_DIR / name)


def save_metadata(payload: Dict[str, Any]) -> None:
    MODEL_DIR.mkdir(exist_ok=True, parents=True)
    with (MODEL_DIR / "metadata.json").open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
