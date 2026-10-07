from __future__ import annotations

from typing import Any, Dict, List


def evaluate_security_rules(event: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []

    if int(event.get("failed_logins", 0)) > 5:
        reasons.append("High number of failed logins")
    if int(event.get("request_count", 0)) > 300:
        reasons.append("High request frequency")
    if int(event.get("login_hour", 0)) in {0, 1, 2, 3, 4, 5}:
        reasons.append("Unusual login time")
    if int(event.get("session_duration", 0)) > 180:
        reasons.append("Long session duration")
    if str(event.get("authentication_status", "")).lower() == "failed":
        reasons.append("Authentication failure detected")
    if int(event.get("bytes_sent", 0)) > 75000 or int(event.get("bytes_received", 0)) > 75000:
        reasons.append("Unusual data transfer volume")

    return reasons
