from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    events = relationship("SecurityEvent", back_populates="user")


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_ip = Column(String(50), nullable=True)
    destination_ip = Column(String(50), nullable=True)
    login_attempts = Column(Integer, default=0)
    failed_logins = Column(Integer, default=0)
    request_count = Column(Integer, default=0)
    session_duration = Column(Integer, default=0)
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    login_hour = Column(Integer, default=0)
    country = Column(String(80), default="unknown")
    device_type = Column(String(50), default="desktop")
    protocol = Column(String(30), default="HTTPS")
    port_category = Column(String(30), default="standard")
    authentication_status = Column(String(30), default="success")
    previous_activity = Column(String(50), default="normal")
    prediction = Column(String(30), default="normal")
    risk_score = Column(Integer, default=0)
    severity = Column(String(30), default="low")
    reasons = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="events")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    severity = Column(String(30), default="low")
    risk_score = Column(Integer, default=0)
    details = Column(Text, default="")
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(200), nullable=False)
    details = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(80), nullable=False)
    version = Column(String(30), default="v1")
    accuracy = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)
    dataset_size = Column(Integer, default=0)
    trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
