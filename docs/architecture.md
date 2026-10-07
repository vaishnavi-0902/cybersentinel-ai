# Architecture Overview

CyberSentinel AI follows a layered architecture.

## Layers

1. Presentation layer: Streamlit dashboard
2. Application layer: FastAPI backend
3. Security and ML layer: preprocessing, feature engineering, model prediction, rules
4. Data layer: PostgreSQL and file-based dataset storage
5. Deployment layer: Docker, Compose, Kubernetes, Jenkins

## Data flow

- Users authenticate and access dashboard
- Analysts upload or select security dataset
- Backend validates and processes data
- ML model predicts suspicious vs normal activity
- Risk engine calculates score and severity
- Alerts and events are saved to database
- Dashboard displays charts, logs, and security insights
