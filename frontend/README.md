# Next.js Frontend

This frontend replaces Streamlit with a modern Next.js UI and calls FastAPI directly for both auth and validation APIs.

## Setup

1. Create a local env file:
   - Copy `.env.example` to `.env.local`
2. Fill required values:
   - `NEXT_PUBLIC_FASTAPI_BASE_URL` (usually `http://127.0.0.1:8000`)

## Run

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Auth + Protected Routes

- Login page: `/login`
- Protected dashboard pages: `/dashboard/*`
- Authentication uses backend endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/logout`
  - `GET /auth/me`

## Target Country Selection

Validation forms support country-specific inference with:
- `honduras` (default)
- `ecuador`

The frontend sends `target_country` to backend validation endpoints so dialect model,
OCR blacklist, and visual anchors switch to the selected country profile.

## FastAPI Prerequisite

The backend (`services.api_server`) must be running for validation calls to succeed.

```bash
uvicorn services.api_server:app --host 0.0.0.0 --port 8000
```

Optional backend environment variables:
- `AUTH_SECRET` for token signing (set a strong value in production)
- `FRONTEND_ORIGINS` for CORS allowed origins

## Deploy on AWS Amplify

This frontend includes an `amplify.yaml` in the `frontend` folder.

### Amplify build target
- App root: `frontend`
- Build command: `npm run build`
- Artifacts: `.next`

### Required Amplify environment variable
- `NEXT_PUBLIC_FASTAPI_BASE_URL` = your public FastAPI API URL
  - Example: `https://api.your-domain.com`

### Backend CORS reminder
Your FastAPI server must allow your Amplify domain in `FRONTEND_ORIGINS`, for example:
- `https://main.xxxxxx.amplifyapp.com`
- or your custom frontend domain
