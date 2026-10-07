# Docker Instructions

## Build backend image

`docker build -t cybersentinel-backend .`

## Run backend

`docker run -p 8000:8000 cybersentinel-backend`

## Docker Compose

`docker compose up --build`

This starts the backend, frontend, and PostgreSQL services together.
