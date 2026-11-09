# YeabTech Sovereign Electronic Invoicing Platform

A multi-tenant electronic invoicing and ERP platform developed by
YeabTech Networking and Trading PLC.

## Architecture

- Backend: FastAPI
- Database: PostgreSQL
- Tenant isolation: PostgreSQL Row-Level Security (RLS)
- Frontend: React and TypeScript
- Background processing: Celery
- Message broker: Redis
- ERP integration: Tryton
- Containerization: Docker and Docker Compose

## Architecture Principles

1. PostgreSQL is the authoritative source for fiscal records.
2. Every tenant-scoped table must enforce PostgreSQL RLS.
3. Fiscal events and audit history are append-only.
4. Invoice submission uses the Transactional Outbox pattern.
5. FastAPI must not publish Celery tasks directly inside HTTP requests.
6. MoR integration is isolated behind a dedicated integration layer.
7. Credentials, private keys and certificates must never be committed.

## Project Status

Development environment preparation.

## Documentation

See the `docs/` directory for architecture, compliance,
technical decisions and development documentation.
