import os
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="CyberSentinel AI", page_icon="🛡️", layout="wide")


def auth_headers():
    token = st.session_state.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def get_json(endpoint: str, params: Dict[str, Any] | None = None):
    response = requests.get(f"{API_URL}{endpoint}", headers=auth_headers(), params=params, timeout=20)
    if response.status_code in {401, 403}:
        st.warning("Session expired. Please log in again.")
        st.session_state.pop("token", None)
        return {}
    response.raise_for_status()
    return response.json()


def post_json(endpoint: str, payload: Dict[str, Any]):
    response = requests.post(f"{API_URL}{endpoint}", json=payload, headers=auth_headers(), timeout=20)
    if response.status_code in {401, 403}:
        st.warning("Session expired. Please log in again.")
        st.session_state.pop("token", None)
        return {}
    response.raise_for_status()
    return response.json()


def login_view():
    st.title("CyberSentinel AI")
    st.caption("Defensive cybersecurity monitoring, anomaly detection, and risk scoring")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            try:
                result = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password}, timeout=20)
                if result.status_code != 200:
                    st.error("Login failed. Please check credentials.")
                    return
                token = result.json()["access_token"]
                st.session_state["token"] = token
                st.success("Login successful")
                st.rerun()
            except Exception as exc:
                st.error(f"Connection error: {exc}")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("New username")
            email = st.text_input("Email")
            new_password = st.text_input("Create password", type="password")
            role = st.selectbox("Role", ["viewer", "analyst", "admin"])
            submitted = st.form_submit_button("Register")
        if submitted:
            try:
                result = requests.post(
                    f"{API_URL}/auth/register",
                    json={"username": new_username, "email": email, "password": new_password, "role": role},
                    timeout=20,
                )
                if result.status_code != 200:
                    st.error(result.json().get("detail", "Registration failed."))
                    return
                st.success("Registration successful. Please log in.")
            except Exception as exc:
                st.error(f"Connection error: {exc}")


def render_dashboard():
    stats = get_json("/statistics")
    events = get_json("/events")
    if not stats:
        st.info("No data is available yet. Upload a dataset or run the training script.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", stats.get("total_events", 0))
    col2.metric("Suspicious", stats.get("suspicious_events", 0))
    col3.metric("High Risk", stats.get("high_risk_events", 0))
    col4.metric("Avg Risk", round(stats.get("average_risk_score", 0), 2))

    if events:
        df = pd.DataFrame(events)
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])

        st.subheader("Security overview")
        fig = px.histogram(df, x="risk_score", nbins=15, title="Risk score distribution")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recent security events")
        st.dataframe(df[["id", "prediction", "risk_score", "severity", "created_at"]].head(12), use_container_width=True)

        if "prediction" in df.columns:
            pred_counts = df["prediction"].value_counts()
            fig2 = px.bar(pred_counts, x=pred_counts.index, y=pred_counts.values, title="Normal vs Suspicious")
            st.plotly_chart(fig2, use_container_width=True)


def render_upload():
    st.subheader("Upload security dataset")
    uploaded = st.file_uploader("CSV or JSON dataset", type=["csv", "json"])
    if uploaded is not None:
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        try:
            response = requests.post(f"{API_URL}/upload", files=files, headers=auth_headers(), timeout=60)
            st.write(response.json())
        except Exception as exc:
            st.error(f"Upload failed: {exc}")


def render_analysis():
    st.subheader("Threat analysis")
    with st.form("predict_form"):
        failed_logins = st.number_input("Failed logins", min_value=0, value=0)
        request_count = st.number_input("Request count", min_value=0, value=100)
        session_duration = st.number_input("Session duration", min_value=0, value=60)
        login_hour = st.number_input("Login hour", min_value=0, max_value=23, value=2)
        bytes_sent = st.number_input("Bytes sent", min_value=0, value=15000)
        submitted = st.form_submit_button("Run analysis")

    if submitted:
        payload = {
            "failed_logins": int(failed_logins),
            "request_count": int(request_count),
            "session_duration": int(session_duration),
            "login_hour": int(login_hour),
            "bytes_sent": int(bytes_sent),
            "bytes_received": 20000,
            "login_attempts": 2,
            "country": "USA",
            "device_type": "desktop",
            "protocol": "HTTPS",
            "port_category": "standard",
            "authentication_status": "failed" if failed_logins > 0 else "success",
            "previous_activity": "normal",
        }
        result = post_json("/predict", payload)
        st.json(result)


def render_alerts():
    alerts = get_json("/alerts")
    if alerts:
        df = pd.DataFrame(alerts)
        st.dataframe(df, use_container_width=True)

        alert_id = st.selectbox("Select alert to update", options=df["id"].tolist() if not df.empty else [])
        if alert_id:
            new_status = st.selectbox("Set status", ["open", "investigating", "resolved"])
            if st.button("Update alert status"):
                resp = requests.patch(f"{API_URL}/alerts/{alert_id}/status?status_value={new_status}", headers=auth_headers(), timeout=20)
                if resp.ok:
                    st.success("Alert status updated")
                else:
                    st.error(resp.json().get("detail", "Update failed"))
    else:
        st.info("No alerts yet.")


def render_model():
    model_info = get_json("/model/info")
    metrics = get_json("/metrics")
    st.subheader("Current model metadata")
    st.json(model_info)
    st.subheader("Performance metrics")
    st.json(metrics)


def render_health():
    st.subheader("System health")
    health = get_json("/health")
    st.json(health)


def main():
    if "token" not in st.session_state:
        login_view()
        return

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select page", ["Dashboard", "Upload", "Threat Analysis", "Alerts", "ML Model", "System Health"])
    if st.sidebar.button("Logout"):
        st.session_state.pop("token", None)
        st.rerun()

    if page == "Dashboard":
        render_dashboard()
    elif page == "Upload":
        render_upload()
    elif page == "Threat Analysis":
        render_analysis()
    elif page == "Alerts":
        render_alerts()
    elif page == "ML Model":
        render_model()
    elif page == "System Health":
        render_health()


if __name__ == "__main__":
    main()
