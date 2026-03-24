# Next.js Migration Plan

## Goal
Migrate from the current Streamlit frontend to a production-ready Next.js frontend while keeping FastAPI as the ML inference backend.

## Current State
- Frontend: `app.py` (Streamlit)
- Backend API: `services/api_server.py` (FastAPI)
- Core inference: `video_validator.py`

## Target Architecture
- `frontend/` (Next.js App Router + TypeScript)
- Existing Python backend for model execution
- Next.js server routes acting as a secure BFF layer between browser and FastAPI

## Migration Phases

### Phase 1 - Foundation
- Scaffold Next.js app.
- Add auth (NextAuth) with protected routes.
- Add environment setup (`NEXTAUTH_SECRET`, API base URL).
- Build dashboard shell and base navigation.

### Phase 2 - Feature Parity
- Implement text/image/audio/video validation UI pages.
- Route frontend requests via Next.js API routes.
- Mirror Streamlit mode behavior with modular React components.

### Phase 3 - Security Hardening
- Enforce authenticated access to protected routes.
- Add input validation and rate limiting in BFF routes.
- Restrict CORS at FastAPI to frontend origin only.
- Add request logging and audit trails.

### Phase 4 - Async Jobs for Large Videos
- Introduce job-based flow (`/jobs`, `/jobs/{id}`, `/jobs/{id}/result`).
- Optional queue (Redis + worker) for heavy validations.
- Add retry, timeout, and cancellation handling.

### Phase 5 - Cutover
- Run Streamlit and Next.js in parallel for validation.
- Compare outputs on the same sample set.
- Switch traffic to Next.js frontend.
- Keep Streamlit as fallback for a short period.

## Data and API Design Decisions
- Do not expose FastAPI directly to browser clients for sensitive operations.
- Browser calls Next.js server route; Next.js route calls FastAPI.
- Standardize response payload shape in one place (BFF layer).

## Security Checklist
- Strong `NEXTAUTH_SECRET`.
- Session-based route protection.
- Server-side env var usage only for backend URLs and secrets.
- File type/size validation before forwarding requests.
- Rate limiting on validation endpoints.

## Rollback Plan
- Keep Streamlit app unchanged during migration.
- If regression appears, point users back to Streamlit while fixing Next.js.

## Deliverables in This Repository
- `frontend/`: new Next.js UI and auth shell.
- `docs/API_CONTRACTS.md`: frontend-backend interface contracts.
