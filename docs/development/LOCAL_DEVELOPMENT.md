# YeabTech Local Development Guide

## Environment
- Windows host: Docker Desktop and Docker Compose.
- Development: VS Code Dev Container.
- Python: 3.12.
- Backend: FastAPI.
- Database: PostgreSQL 18.
- ORM: SQLAlchemy 2.x with asyncpg.
- Migrations: Alembic.
- Broker: Redis 7.

## Docker operations
Run Docker Compose commands in Windows PowerShell, outside the Dev Container.
Start services: docker compose up -d postgres redis
Check services: docker compose ps
Stop services: docker compose stop postgres redis

## Backend operations
Run these commands inside the Dev Container, from /workspace:
- make backend-install
- make backend-run
- make backend-test
- make backend-lint
- make validate

## API endpoints
- http://localhost:8000/
- http://localhost:8000/api/v1/health/live
- http://localhost:8000/api/v1/health/ready
- http://localhost:8000/docs

## Security
- Never commit .env or production credentials.
- Never commit private keys or certificates.
- Do not use production taxpayer data in development.

## Development boundary
The SRS and outstanding MoR clarifications are not finalized.
This repository currently contains technical scaffolding only.
Do not implement fiscal workflows, final domain models, tenant authorization policies, or production MoR integration before their requirements are approved.
