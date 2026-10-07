from __future__ import annotations

from typing import List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_columns = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = [col for col in X.columns if col not in numeric_columns]

    transformers = []
    if numeric_columns:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_columns,
            )
        )
    if categorical_columns:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_columns,
            )
        )

    return ColumnTransformer(transformers=transformers, remainder="drop")


def get_feature_columns() -> List[str]:
    return [
        "failed_logins",
        "request_count",
        "session_duration",
        "bytes_sent",
        "bytes_received",
        "login_hour",
        "login_attempts",
        "country",
        "device_type",
        "protocol",
        "port_category",
        "authentication_status",
        "previous_activity",
    ]
