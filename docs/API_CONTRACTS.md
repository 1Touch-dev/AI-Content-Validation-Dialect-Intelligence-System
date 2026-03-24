# API Contracts (Next.js <-> FastAPI)

## Overview
The browser should call Next.js API routes. Next.js routes call FastAPI endpoints.

## Environment
- `FASTAPI_BASE_URL` (Next.js server env): example `http://127.0.0.1:8000`

## Contract 1: Validate Video by Path

### Browser -> Next.js
- `POST /api/validate`

Request body:
```json
{
  "videoPath": "C:/absolute/path/to/video.mp4",
  "expectedTopic": "Honduran football player"
}
```

Response body:
```json
{
  "ok": true,
  "data": {
    "transcript": "....",
    "dialect_prediction": "Honduras",
    "dialect_confidence": 0.93,
    "content_match_score": 0.81,
    "validation_status": "PASS"
  }
}
```

Error body:
```json
{
  "ok": false,
  "error": "Human readable error"
}
```

### Next.js -> FastAPI
- `POST /validate-video`

Request body:
```json
{
  "video_path": "C:/absolute/path/to/video.mp4",
  "expected_topic": "Honduran football player"
}
```

Response body:
```json
{
  "transcript": "....",
  "dialect_prediction": "Honduras",
  "dialect_confidence": 0.93,
  "content_match_score": 0.81,
  "validation_status": "PASS"
}
```

## Contract 2: Future Upload + Job Flow (Planned)
- `POST /api/uploads` -> returns upload URL/path
- `POST /api/jobs` -> creates validation job
- `GET /api/jobs/:id` -> status
- `GET /api/jobs/:id/result` -> final validation result

These are planned for large files and multi-user concurrency.
