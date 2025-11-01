# ADR-0001: Dashboard Stack Selection

Date: 2025-11-01

Status: Accepted

Context

The MamboLite core is Python-based (CSV processing, Pandas, packaging). Phase 3 introduces a web dashboard with API connectors, scheduled sync, mapping/dedupe server-side, and exports. We must choose a baseline stack that balances development speed, reuse of existing code, operational simplicity, and future growth.

Decision

- Frontend: Next.js (React) + TypeScript
- Backend API: FastAPI (Python)
- Workers/Queue: Celery (Python) + Redis
- Database: PostgreSQL
- Auth: Auth0 (managed)
- Hosting: Vercel (frontend), Render/Fly.io (API + workers), managed Postgres (e.g., Neon/Railway/Render), managed Redis (Upstash/Redis Cloud)

Rationale

- Leverages existing Python expertise and enables reuse of MamboLite cleaning/mapping logic server-side (no reimplementation in Node).
- FastAPI provides modern async APIs, excellent typing, and performance; rich ecosystem with SQLAlchemy/SQLModel and Pydantic.
- Celery + Redis is a mature background job stack for periodic and long-running syncs.
- Next.js is a widely adopted React framework with great DX and a smooth path to hosted deployments and auth integrations.
- Auth0 reduces auth complexity (user accounts, orgs, social/enterprise IdPs, secure session flows) so we can focus on connectors and data quality.

Consequences

- Unifies the server-side language as Python (API + workers), simplifying shared models and utilities.
- Requires basic DevOps for multi-service deploys (frontend + API + workers + DB + Redis). We’ll start with managed providers to reduce ops burden.
- Future integrations in Node are still possible behind the API if needed; however, core remains Python-first.

Implementation Outline

1. Repos/Dirs: create `/dashboard/web` (Next.js), `/dashboard/api-python` (FastAPI), `/dashboard/workers` (Celery), `/dashboard/shared` (types/models)
2. Infra: provision Postgres + Redis; set secrets in env (Auth0, DB, Redis)
3. CI: basic build/test workflows for web and API; deploy hooks (manual initially)
4. MVP scopes: Auth, connectors (Google, Microsoft, HubSpot), background sync, mapping/dedupe, exports

