from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd


random.seed(42)
np.random.seed(42)


def generate_dataset(output_path: str | Path, rows: int = 5000) -> pd.DataFrame:
    countries = ["USA", "UK", "India", "Germany", "Canada", "Brazil", "Japan", "Australia"]
    devices = ["desktop", "laptop", "mobile", "tablet"]
    protocols = ["HTTPS", "SSH", "SMTP", "FTP", "DNS"]
    port_categories = ["standard", "admin", "restricted", "database"]
    previous_activity = ["normal", "low_activity", "suspicious", "new_device"]
    statuses = ["success", "failed", "success", "failed"]

    data = []
    for i in range(rows):
        login_hour = random.randint(0, 23)
        failed_logins = random.randint(0, 12)
        request_count = random.randint(10, 800)
        session_duration = random.randint(5, 220)
        bytes_sent = random.randint(1000, 120000)
        bytes_received = random.randint(1000, 180000)
        is_suspicious = random.random() < 0.28

        if is_suspicious:
            login_hour = random.choice([0, 1, 2, 3, 4, 5, 22, 23])
            failed_logins = random.randint(4, 12)
            request_count = random.randint(250, 900)
            session_duration = random.randint(90, 260)
            bytes_sent = random.randint(40000, 200000)
            bytes_received = random.randint(45000, 250000)
            previous_activity_value = "suspicious"
            authentication_status = "failed"
            label = "suspicious"
        else:
            previous_activity_value = random.choice(previous_activity)
            authentication_status = random.choice(statuses)
            label = "normal"

        row = {
            "timestamp": pd.Timestamp("2024-01-01") + pd.to_timedelta(random.randint(0, 365), unit="D") + pd.to_timedelta(random.randint(0, 23), unit="h") + pd.to_timedelta(random.randint(0, 59), unit="m"),
            "user_id": f"user_{random.randint(1000, 9999)}",
            "source_ip": f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}",
            "destination_ip": f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}",
            "login_attempts": random.randint(1, 12),
            "failed_logins": failed_logins,
            "request_count": request_count,
            "session_duration": session_duration,
            "bytes_sent": bytes_sent,
            "bytes_received": bytes_received,
            "login_hour": login_hour,
            "country": random.choice(countries),
            "device_type": random.choice(devices),
            "protocol": random.choice(protocols),
            "port_category": random.choice(port_categories),
            "authentication_status": authentication_status,
            "previous_activity": previous_activity_value,
            "label": label,
        }
        data.append(row)

    df = pd.DataFrame(data)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df


if __name__ == "__main__":
    generate_dataset(Path(__file__).with_name("sample_security_logs.csv"), rows=5000)
    print("Generated 5000 sample cybersecurity records at data/sample_security_logs.csv")
