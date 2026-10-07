# API Guide

The backend exposes REST endpoints for authentication, prediction, upload, alerts, and statistics.

## Authentication

- POST /auth/register
- POST /auth/login

## Monitoring

- GET /health
- GET /statistics
- GET /metrics
- GET /model/info

## Security processing

- POST /predict
- POST /predict/batch
- POST /upload
- GET /events
- GET /alerts

FastAPI automatically generates OpenAPI documentation at `/docs`.
