from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _register_and_login(username: str, email: str = None, password: str = "securepass123"):
    email = email or f"{username}@demo.com"
    register_response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password, "role": "analyst"},
    )
    assert register_response.status_code in {200, 400}

    login_response = client.post("/auth/login", json={"username": username, "password": password})
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    token = _register_and_login("analyst_demo")
    assert isinstance(token, str)
    assert len(token) > 20


def test_predict_endpoint():
    response = client.post(
        "/predict",
        json={
            "failed_logins": 8,
            "request_count": 500,
            "session_duration": 120,
            "login_hour": 2,
            "bytes_sent": 50000,
            "bytes_received": 30000,
            "login_attempts": 7,
            "country": "USA",
            "device_type": "desktop",
            "protocol": "HTTPS",
            "port_category": "standard",
            "authentication_status": "failed",
            "previous_activity": "suspicious",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction"] in {"normal", "suspicious"}
    assert 0 <= payload["risk_score"] <= 100


def test_upload_csv_success():
    token = _register_and_login("csv_uploader_demo")
    csv_content = "\ufefftimestamp, user_id, source_ip, destination_ip, login_attempts, failed_logins, request_count, session_duration, bytes_sent, bytes_received, login_hour, country, device_type, protocol, port_category, authentication_status, previous_activity, label\n2024-01-01 00:00:00,1,10.0.0.1,10.0.0.2,5,2,200,120,5000,4000,3,USA,desktop,HTTPS,standard,failed,suspicious,suspicious\n2024-01-01 01:00:00,2,10.0.0.3,10.0.0.2,1,0,40,50,3000,2000,7,USA,laptop,HTTPS,standard,success,normal,normal\n"

    response = client.post(
        "/upload",
        files={"file": ("train_and_test2.csv", csv_content.encode("utf-8-sig"), "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["rows"] == 2
    assert payload["columns"] >= 18
    assert payload["column_names"]
    assert payload["preview"]
    assert payload["message"] == "Dataset processed successfully"


def test_upload_csv_missing_required_features_returns_helpful_message():
    token = _register_and_login("csv_incompat_demo")
    csv_content = "id,name,score\n1,alpha,50\n2,beta,60\n"

    response = client.post(
        "/upload",
        files={"file": ("incompatible.csv", csv_content.encode("utf-8"), "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "warning"
    assert "current CyberSentinel model" in payload["message"]
    assert "Required features" in payload["message"]
    assert "Detected columns" in payload["message"]
    assert payload["detected_columns"] == ["id", "name", "score"]
