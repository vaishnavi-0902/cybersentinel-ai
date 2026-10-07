from backend.app.security.rules import evaluate_security_rules


def test_security_rules_flag_suspicious_activity():
    event = {
        "failed_logins": 8,
        "request_count": 500,
        "session_duration": 220,
        "login_hour": 2,
        "bytes_sent": 90000,
        "bytes_received": 100000,
        "authentication_status": "failed",
    }

    reasons = evaluate_security_rules(event)
    assert "High number of failed logins" in reasons
    assert "High request frequency" in reasons
    assert "Unusual login time" in reasons
