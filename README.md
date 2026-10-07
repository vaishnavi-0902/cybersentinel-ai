# CyberSentinel AI

CyberSentinel AI is a defensive cybersecurity monitoring project designed for academic demonstration and final-year portfolio use. It combines a FastAPI backend, machine learning threat analysis, a Streamlit dashboard, and deployment-ready architecture patterns into a practical SOC-style system.

## Project overview

The project simulates a security operations environment where users can register, analyze security events, upload datasets, review risk scores, and manage alerts. Machine learning models identify suspicious patterns, and the system stores events and alerts for later review.

## Objectives

- detect suspicious cybersecurity activity using simulated defensive datasets
- calculate risk scores and classify event severity
- provide a usable dashboard for monitoring and analysis
- expose a secure REST API for authentication and prediction workflows
- demonstrate deployment readiness with Docker, Kubernetes, Jenkins, and CI/CD concepts
- provide a beginner-friendly implementation that still feels production-oriented

## Key features

- JWT-based authentication and protected API routes
- CSV/JSON dataset upload support
- simulated event generation and risk analysis
- Random Forest classification for attack detection
- Isolation Forest anomaly detection for suspicious behavior
- alert generation and lifecycle updates
- dashboard visualizations for trends, risk distribution, and summary metrics
- automated tests for API validation
- container and orchestration scaffolds for real-world deployment discussion

## Architecture

User -> Streamlit dashboard -> FastAPI API -> ML services + SQL database

## Tech stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- Streamlit
- scikit-learn
- Plotly
- SQLite for local development
- Docker and Docker Compose
- Kubernetes manifests
- Jenkins pipeline

## Quick start

### 1) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2) Train the model

```powershell
python -m ml.train
```

### 3) Start the backend

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### 4) Start the frontend

```powershell
streamlit run frontend/app.py
```

### 5) Optional Docker runtime

```powershell
docker compose up --build
```

### 6) Optional Kubernetes deployment

```powershell
kubectl apply -f k8s/
```

## Project structure

- backend/app: API, routes, auth, models, config
- frontend: Streamlit dashboard
- ml: training and prediction pipeline
- data: dataset generation and sample event data
- models: saved ML artifacts
- tests: automated functional checks
- docs: architecture, viva, security, deployment, and presentation materials
- docker: container configuration
- k8s: Kubernetes manifests
- Jenkinsfile: CI/CD flow

## Demo workflow

1. Register a user account.
2. Log in to the dashboard.
3. Upload a security dataset or use the generated sample data.
4. Run threat analysis.
5. Review risk score distribution and recent alerts.
6. Check model metrics and overall health status.

## Documentation

This project includes supporting documents in the docs folder for:

- architecture overview
- API documentation
- Docker guidance
- Kubernetes deployment
- security considerations
- testing strategy
- viva/presentation questions
- development progress notes

## Important note

This project is for defensive, simulated, educational use only. It is designed to demonstrate cybersecurity monitoring and threat detection principles without performing unauthorized or harmful actions.
