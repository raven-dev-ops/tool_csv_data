# MamboLite Phase 3 – Web Dashboard & API Connectors (Proposal)

## Objectives

- Provide a secure web dashboard where users can:
  - Create accounts and manage organization/user settings
  - Connect contact sources (Google People, Microsoft Graph, HubSpot)
  - Trigger/schedule background sync
  - View deduplicated contacts and export CSV/XLSX

## Recommended Stack

- Frontend: Next.js (React) + TypeScript
- Backend API: FastAPI (Python) or Node (NestJS/Express) – choose one
- Database: PostgreSQL (managed)
- Queue/Workers: Redis + RQ (Python) or BullMQ (Node)
- Auth: Auth0/Clerk/Cognito (managed)
- Hosting: Vercel/Netlify (frontend), Fly.io/Render/Heroku (API), Railway/Supabase for DB

## High-Level Architecture

- next/ (frontend): Auth UI, connectors UI, contacts list, exports
- api/ (backend): REST endpoints, OAuth redirects, sync jobs, mapping/dedupe pipeline
- workers/: background job processors consuming a queue
- db/: migration scripts (Alembic/Prisma)

## Directory Layout (Monorepo)

```
/dashboard
  /web              # Next.js app (pages/app router, auth UI)
  /api-python       # FastAPI app (OAuth flows, REST endpoints)
  /api-node         # Alternative Node API (NestJS/Express)
  /workers          # Background workers (Python or Node)
  /infra            # IaC scripts (optional)
  /shared           # Shared libs (types, schema, utils)
```

## Key Flows

- OAuth Connectors
  - Start: frontend -> backend auth endpoint -> provider consent
  - Store: encrypted refresh tokens
  - Sync: schedule background jobs to fetch contacts (paginated, rate-limited)

- Mapping & Dedupe
  - Reuse MamboLite mapping/normalization
  - Persist unified schema tables and deduplicated view

- Exports
  - On-demand: generate CSV/XLSX and provide signed URL download

## Core API Endpoints (Examples)

- POST /connectors/google/start
- GET /connectors/google/callback
- POST /sync/run (body: connector, account_id)
- GET /contacts?limit=50&offset=0
- POST /exports (body: format="csv|xlsx") -> returns download URL

## Data Model Outline

- accounts(id, owner_id, created_at)
- users(id, email, role, account_id)
- connectors(id, account_id, provider, status, created_at)
- credentials(id, connector_id, enc_refresh_token, scopes, expires_at)
- contacts_raw(id, connector_id, payload, fetched_at)
- contacts_unified(id, account_id, first_name, last_name, ...)
- contacts_deduped(view/materialized)
- sync_runs(id, connector_id, status, started_at, finished_at, counts)

## Security & Privacy

- Store tokens encrypted (KMS/Secrets Manager)
- Least-privilege OAuth scopes
- Audit logging for auth, sync, exports
- PII minimization in logs

## MVP Milestones

1) Platform & Auth
2) Connectors & OAuth (Google, Microsoft, HubSpot read-only)
3) Sync & Mapping (background jobs)
4) Dashboard UX (status, contacts, exports) + UAT

## Notes

- Start with one backend (FastAPI recommended) and omit api-node initially
- Treat dashboard repo as separate service; this repo carries plans and release automation templates

