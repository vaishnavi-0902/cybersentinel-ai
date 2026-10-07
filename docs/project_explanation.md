# CyberSentinel Project Explanation

## What is CyberSentinel?

CyberSentinel is a defensive cybersecurity project that monitors security activity, identifies suspicious behavior, and explains risk using simple, understandable rules and machine learning.

## Why use machine learning?

Machine learning helps discover patterns that are difficult to detect manually. It can identify unusual login timings, high request volume, and suspicious combinations of user activity.

## How does anomaly detection work?

Anomaly detection learns the normal pattern of events and marks unusual activity as suspicious. Isolation Forest is useful here because it isolates rare points instead of requiring labels for all events.

## How does risk scoring work?

Risk is calculated by combining ML confidence, anomaly score, and rule-based security checks such as failed logins or abnormal request volume. A risk value between 0 and 100 is then mapped to low, medium, high, or critical severity.

## How does FastAPI talk to Streamlit?

Streamlit sends HTTP requests to the FastAPI backend, which handles authentication, dataset upload, prediction, and reporting. The frontend displays processed data and charts for the user.

## Why PostgreSQL?

PostgreSQL is a reliable relational database suitable for storing users, events, alerts, and model metadata in a structured way. It supports business logic and future reporting work.

## What does Docker do?

Docker packages the app into containers so it can be run consistently across environments. This makes local development, CI/CD, and deployment easier.

## What does Kubernetes do?

Kubernetes orchestrates containers. It manages deployments, services, scaling, and health checks for the system.

## What does Jenkins do?

Jenkins automates building, testing, linting, and deployment tasks so the system can be validated repeatedly.
