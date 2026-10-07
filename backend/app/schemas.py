from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    role: str = "viewer"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SecurityEventBase(BaseModel):
    timestamp: Optional[datetime] = None
    user_id: Optional[int] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    login_attempts: int = 0
    failed_logins: int = 0
    request_count: int = 0
    session_duration: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    login_hour: int = 0
    country: str = "unknown"
    device_type: str = "desktop"
    protocol: str = "HTTPS"
    port_category: str = "standard"
    authentication_status: str = "success"
    previous_activity: str = "normal"


class PredictionRequest(SecurityEventBase):
    pass


class PredictionResponse(BaseModel):
    prediction: str
    risk_score: int
    severity: str
    anomaly_score: float
    reasons: List[str]


class EventResponse(SecurityEventBase):
    id: int
    prediction: Optional[str] = None
    risk_score: Optional[int] = None
    severity: Optional[str] = None
    reasons: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertResponse(BaseModel):
    id: int
    event_id: Optional[int]
    alert_id: str
    severity: str
    risk_score: int
    details: str
    status: str
    created_at: datetime


class StatsResponse(BaseModel):
    total_events: int
    normal_events: int
    suspicious_events: int
    high_risk_events: int
    critical_alerts: int
    average_risk_score: float
