import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.config import PROJECT_ROOT, settings
from backend.app.database import get_db
from backend.app.models import Alert, SecurityEvent, User
from backend.app.schemas import PredictionRequest, PredictionResponse, StatsResponse
from backend.app.security.auth import get_current_user
from backend.app.security.rules import evaluate_security_rules
from backend.app.services.ingestion_service import (
    describe_dataset,
    parse_uploaded_csv,
    parse_uploaded_json,
    validate_and_clean_data,
    validate_uploaded_columns,
)
from backend.app.services.ml_service import batch_predict, load_metadata, predict_event

logger = logging.getLogger("cybersentinel")

router = APIRouter(tags=["core"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "cybersentinel-ai"}


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    try:
        return predict_event(payload.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="Model files are missing. Train the model first.") from exc


@router.post("/predict/batch")
def predict_batch(payloads: List[PredictionRequest]):
    return {"results": [predict_event(item.model_dump()) for item in payloads]}


@router.post("/upload")
def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Uploaded file is missing a filename")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in {".csv", ".json"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension '{file_ext}'. Only CSV and JSON files are allowed.")

    contents = file.file.read()
    if not contents or not contents.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        if file_ext == ".csv":
            df = parse_uploaded_csv(file.filename, contents)
        else:
            df = parse_uploaded_json(file.filename, contents)
    except ValueError as exc:
        logger.exception("Dataset upload parse failed for %s", file.filename)
        message = str(exc)
        if settings.app_env == "development":
            raise HTTPException(status_code=400, detail=message) from exc
        raise HTTPException(status_code=400, detail="Could not parse uploaded file. Check the format.") from exc
    except Exception as exc:
        logger.exception("Unexpected dataset upload error for %s", file.filename)
        raise HTTPException(status_code=400, detail=f"Could not parse uploaded file. Actual error: {exc}") from exc

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    dataset_info = describe_dataset(df)
    column_validation = validate_uploaded_columns(df)

    if not column_validation["is_compatible"]:
        return {
            "filename": file.filename,
            "rows": dataset_info["rows"],
            "columns": dataset_info["columns"],
            "column_names": dataset_info["column_names"],
            "missing_values": dataset_info["missing_values"],
            "preview": dataset_info["preview"],
            "status": "warning",
            "message": (
                "Dataset uploaded successfully.\n\n"
                "However, this dataset does not contain the features required by the current CyberSentinel model.\n\n"
                "Required features:\n"
                f"{column_validation['required_features']}\n\n"
                "Detected columns:\n"
                f"{column_validation['detected_columns']}\n\n"
                "You can either:\n"
                "1. Upload the CyberSentinel sample dataset, or\n"
                "2. Map the available columns to the required features."
            ),
            "required_features": column_validation["required_features"],
            "detected_columns": column_validation["detected_columns"],
        }

    try:
        validation = validate_and_clean_data(df)
    except ValueError as exc:
        logger.exception("Dataset validation failed for %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Uploaded dataset is missing required CyberSentinel columns. "
                f"Detected columns: {list(df.columns)}. "
                f"Validation error: {exc}"
            ) if settings.app_env == "development" else "Dataset validation failed. Please upload a compatible CyberSentinel dataset.",
        ) from exc

    cleaned_df = validation["cleaned_df"]

    for _, row in cleaned_df.iterrows():
        payload = row.to_dict()
        event_result = predict_event(payload)
        reasons = "; ".join(event_result["reasons"])
        event = SecurityEvent(
            timestamp=row.get("timestamp"),
            user_id=current_user.id,
            source_ip=str(payload.get("source_ip", "unknown")),
            destination_ip=str(payload.get("destination_ip", "unknown")),
            login_attempts=int(payload.get("login_attempts", 0)),
            failed_logins=int(payload.get("failed_logins", 0)),
            request_count=int(payload.get("request_count", 0)),
            session_duration=int(payload.get("session_duration", 0)),
            bytes_sent=int(payload.get("bytes_sent", 0)),
            bytes_received=int(payload.get("bytes_received", 0)),
            login_hour=int(payload.get("login_hour", 0)),
            country=str(payload.get("country", "unknown")),
            device_type=str(payload.get("device_type", "desktop")),
            protocol=str(payload.get("protocol", "HTTPS")),
            port_category=str(payload.get("port_category", "standard")),
            authentication_status=str(payload.get("authentication_status", "success")),
            previous_activity=str(payload.get("previous_activity", "normal")),
            prediction=event_result["prediction"],
            risk_score=event_result["risk_score"],
            severity=event_result["severity"],
            reasons=reasons,
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        if event_result["risk_score"] >= 80:
            alert = Alert(
                event_id=event.id,
                alert_id=f"ALERT-{event.id}",
                severity=event_result["severity"],
                risk_score=event_result["risk_score"],
                details=reasons,
                status="open",
            )
            db.add(alert)
            db.commit()

    return {
        "filename": file.filename,
        "rows": dataset_info["rows"],
        "columns": dataset_info["columns"],
        "column_names": dataset_info["column_names"],
        "preview": dataset_info["preview"],
        "missing_values": dataset_info["missing_values"],
        "status": "success",
        "message": "Dataset processed successfully",
        "total_records": int(validation["original_rows"]),
        "valid_records": int(validation["valid_rows"]),
        "invalid_records": int(validation["invalid_rows"]),
        "duplicate_records": int(validation["duplicate_rows"]),
    }


@router.get("/events")
def list_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SecurityEvent).order_by(SecurityEvent.created_at.desc()).all()


@router.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/alerts")
def list_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/status")
def update_alert_status(alert_id: int, status_value: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    valid_statuses = {"open", "investigating", "resolved"}
    if status_value.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail="Status must be one of: open, investigating, resolved")
    alert.status = status_value.lower()
    db.commit()
    return {"message": "Alert status updated", "alert_id": alert_id, "status": alert.status}


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = db.query(SecurityEvent).all()
    total = len(events)
    suspicious = sum(1 for e in events if e.prediction == "suspicious")
    normal = sum(1 for e in events if e.prediction == "normal")
    high_risk = sum(1 for e in events if e.risk_score >= 60)
    critical_alerts = db.query(Alert).filter(Alert.severity == "critical").count()
    average_risk = round(sum(e.risk_score for e in events) / total, 2) if total else 0.0
    return {
        "total_events": total,
        "normal_events": normal,
        "suspicious_events": suspicious,
        "high_risk_events": high_risk,
        "critical_alerts": critical_alerts,
        "average_risk_score": average_risk,
    }


@router.get("/model/info")
def model_info():
    return load_metadata() or {"status": "not trained yet", "message": "Run the training script"}


@router.get("/metrics")
def metrics():
    metadata = load_metadata()
    if not metadata:
        return {"status": "not available"}
    return {
        "accuracy": metadata.get("accuracy", 0),
        "precision": metadata.get("precision", 0),
        "recall": metadata.get("recall", 0),
        "f1_score": metadata.get("f1_score", 0),
    }
