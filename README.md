# DevOps Starter (FastAPI + Postgres + Docker)

A minimal, production-minded starter template for deploying a Python FastAPI service with PostgreSQL using Docker and Docker Compose. This repo includes:

- FastAPI application with health and readiness probes
- PostgreSQL database (via docker-compose)
- Prometheus metrics endpoint (/metrics)
- Structured JSON logging to stdout
- Dockerfile for containerization
- docker-compose.yml for local development
- docker-compose.prod.yml snippet to run behind nginx-proxy with automated Let's Encrypt certificates (DigitalOcean-friendly)
- SECURITY.md with security practices

## Quick links
- Health: GET /healthz → {"status": "ok"}
- Readiness (DB check): GET /readyz → {"ready": true|false}
- Root: GET / → {"message": "Hello from FastAPI!"}
- Prometheus metrics: GET /metrics (CONTENT_TYPE_LATEST)

## Tech stack
- Python 3.9 (container base)
- FastAPI
- Uvicorn
- SQLAlchemy
- psycopg (PostgreSQL driver)
- Prometheus client
- Docker, Docker Compose

## Prerequisites
- Docker and Docker Compose installed
- Alternatively, Python 3.9+ and pip if running locally without Docker

## Project structure
- app/main.py — FastAPI app, routes, middleware, DB readiness
- Dockerfile — container build
- docker-compose.yml — local dev stack (api + Postgres)
- docker-compose.prod.yml — production reverse proxy (nginx-proxy + ACME companion) overlay
- requirements.txt — Python dependencies
- SECURITY.md — security notes
- LICENSE — project license

## Environment variables
The app requires a database URL exposed as DATABASE_URL. When using docker-compose, Postgres variables are also used.

Minimum variables:
- DATABASE_URL — SQLAlchemy/psycopg URL, e.g. postgresql+psycopg://postgres:postgres@db:5432/postgres
- POSTGRES_USER — Postgres username (compose)
- POSTGRES_PASSWORD — Postgres password (compose)
- POSTGRES_DB — Postgres database name (compose)

Tip: Create a .env file at the repository root for docker-compose to load. Example:

```
# .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
# SQLAlchemy expects a driver, we use psycopg v3
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/postgres
```

Note: For production, you will likely use a managed DB (e.g., DigitalOcean Managed PostgreSQL) and set DATABASE_URL accordingly.

## Running locally with Docker Compose (recommended)
1) Create .env at project root (see example above).
2) Start the stack:

```
docker compose up --build
```

3) Access the API at http://localhost:8000
- / → Hello message
- /healthz → simple health check
- /readyz → checks DB connectivity (returns ready: true when DB is reachable)
- /metrics → Prometheus metrics

4) Stop the stack:

```
docker compose down
```

Volumes: A named volume pgdata persists PostgreSQL data between runs.

## Running locally with Python (no Docker)
1) Ensure you have a running PostgreSQL you can access, and set DATABASE_URL accordingly (host will not be "db" in this case).
2) Create and activate a virtual environment, then install deps:

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3) Export environment variable:

```
export DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/mydb"
```

4) Run the server:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Production deployment (DigitalOcean example)
This repo includes docker-compose.prod.yml designed to work with:
- nginx-proxy (automated reverse proxy for Docker)
- acme-companion (auto-manage Let's Encrypt certificates)

High-level steps on a Linux VM (e.g., DigitalOcean Droplet):
- Point your domain's A/AAAA records to the droplet's IP
- Install Docker and Docker Compose
- Clone this repository to the server
- Create a .env with your production DATABASE_URL (ideally pointing to a managed DB) and Postgres values if you plan to run Postgres on the same host
- Start/restart nginx-proxy stack if not already running:

```
docker compose -f docker-compose.prod.yml up -d nginx-proxy acme-companion
```

- Start your app service with the required virtual host labels via compose override. You can either:
  - Add your production env/labels into docker-compose.yml under services.api (VIRTUAL_HOST, LETSENCRYPT_HOST, LETSENCRYPT_EMAIL), or
  - Run with both compose files (base + prod):

```
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build api
```

The docker-compose.prod.yml provides environment entries for the api service:
- VIRTUAL_HOST
- LETSENCRYPT_HOST
- LETSENCRYPT_EMAIL

Adjust those values to match your domain(s) before bringing the stack up. nginx-proxy listens on ports 80/443 and routes traffic to the api container's port 8000.

Security notes:
- Do not commit real secrets. Use environment variables or secret managers
- Review SECURITY.md for additional practices
- Consider DO Firewall rules and limit inbound ports to 80/443 and your SSH port
- Use managed Postgres with private networking where possible

## Observability
- Structured JSON logs are emitted to stdout from the application
- Prometheus metrics exposed at /metrics (scrape with your Prometheus instance)

## Development tips
- Modify app/main.py to add routes
- Hot reload with uvicorn --reload when running locally without Docker
- For DB migrations consider adding Alembic (not included by default)

## Troubleshooting
- Readiness probe failing (/readyz → false): verify DATABASE_URL points to a reachable DB and credentials are correct
- Port conflicts: change the mapped port in docker-compose.yml ("8000:8000")
- SSL certificates not issued: ensure DNS records resolve correctly and LETSENCRYPT_HOST matches your domain

## License
This project is licensed under the terms of the LICENSE file in this repository.
