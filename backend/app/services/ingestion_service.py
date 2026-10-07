from __future__ import annotations

import io
import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger("cybersentinel.upload")

REQUIRED_FEATURES = [
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


def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.columns.empty:
        return df
    df.columns = df.columns.astype(str).str.strip()
    return df


def _read_csv_with_fallback(text: str) -> pd.DataFrame:
    for sep in (None, ",", ";"):
        kwargs = {
            "dtype": str,
            "keep_default_na": True,
            "na_values": ["", " ", "NA", "N/A", "null", "None", "none"],
            "skip_blank_lines": True,
        }
        if sep is not None:
            kwargs["sep"] = sep
        try:
            df = pd.read_csv(io.StringIO(text), engine="python" if sep is not None else "python", **kwargs)
            df = normalize_dataframe_columns(df)
            if df.empty:
                raise ValueError("Uploaded CSV contains no data rows.")
            return df
        except Exception:
            continue
    raise ValueError("Unable to detect a valid CSV structure from the uploaded file.")


def parse_uploaded_csv(file_name: str, contents: bytes) -> pd.DataFrame:
    if not contents or not contents.strip():
        raise ValueError("Uploaded file is empty.")

    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = contents.decode(encoding)
            if not text.strip():
                raise ValueError("Uploaded file is empty.")
            df = _read_csv_with_fallback(text)
            if df.empty:
                raise ValueError("Uploaded CSV contains no data rows.")
            return df
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        except ValueError as exc:
            last_error = exc
            raise
        except Exception as exc:
            last_error = exc
            continue

    if last_error is not None:
        raise ValueError(f"Could not parse CSV file '{file_name}': {last_error}") from last_error
    raise ValueError(f"Could not parse CSV file '{file_name}'.")


def parse_uploaded_json(file_name: str, contents: bytes) -> pd.DataFrame:
    try:
        raw_text = contents.decode("utf-8-sig")
        df = pd.read_json(io.StringIO(raw_text))
        df = normalize_dataframe_columns(df)
        if df.empty:
            raise ValueError("Uploaded JSON contains no data rows.")
        return df
    except Exception as exc:
        logger.exception("JSON upload parse failed for %s", file_name)
        raise ValueError(f"Could not parse JSON file '{file_name}': {exc}") from exc


def describe_dataset(df: pd.DataFrame, preview_limit: int = 5) -> Dict[str, Any]:
    preview = df.head(preview_limit).to_dict(orient="records")
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(col) for col in df.columns],
        "preview": preview,
        "missing_values": int(df.isna().sum().sum()),
    }


def validate_uploaded_columns(df: pd.DataFrame) -> Dict[str, Any]:
    detected_columns = [str(col).strip() for col in df.columns]
    missing_required = [feature for feature in REQUIRED_FEATURES if feature not in detected_columns]
    return {
        "required_features": REQUIRED_FEATURES,
        "missing_required_features": missing_required,
        "detected_columns": detected_columns,
        "is_compatible": not missing_required,
    }


def validate_and_clean_data(df: pd.DataFrame) -> dict:
    original_rows = len(df)
    duplicate_rows = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    required_columns = {
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
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for column in ["failed_logins", "request_count", "session_duration", "bytes_sent", "bytes_received", "login_attempts", "login_hour"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["country"] = df["country"].fillna("unknown").astype(str)
    df["device_type"] = df["device_type"].fillna("desktop").astype(str)
    df["protocol"] = df["protocol"].fillna("HTTPS").astype(str)
    df["port_category"] = df["port_category"].fillna("standard").astype(str)
    df["authentication_status"] = df["authentication_status"].fillna("success").astype(str)
    df["previous_activity"] = df["previous_activity"].fillna("normal").astype(str)
    df["label"] = df["label"].fillna("normal").astype(str)
    df = df.dropna(subset=["timestamp"]).reset_index(drop=True)

    return {
        "original_rows": original_rows,
        "valid_rows": len(df),
        "invalid_rows": max(0, original_rows - len(df) - duplicate_rows),
        "duplicate_rows": duplicate_rows,
        "missing_values": int(df.isna().sum().sum()),
        "cleaned_df": df,
    }
