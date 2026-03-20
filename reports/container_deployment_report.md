# AI Video Validation - Container Deployment Report

**Status**: `CONTAINER_DEPLOYMENT_ACTIVE = TRUE`
**Date**: 2026-03-16

## Container Architecture
The native PyTorch pipeline has been securely mapped to a persistent Linux microservice using Docker and `docker-compose`. 

### `Dockerfile`
- **Base Image**: `python:3.12-slim` (Minimizes artifact footprint).
- **System Dependencies**: Installed `ffmpeg` (for Whisper Audio Extraction) and `libgl1` + `libsm6` (for OpenCV/MoviePy Visuals).
- **Python ML Binaries**: Bootstraps explicit CPU-only wheels for `torch` and HuggingFace pipelines avoiding heavy 5GB+ CUDA footprints on local machines.

### `docker-compose.yml`
Provisioned two interconnected local services:
1. **`video-validator-api`** (Port: 8000) -> The FastAPI backend executing `uvicorn` payloads continuously.
2. **`video-validation-dashboard`** (Port: 8501) -> The Streamlit Analytics monitor.

## Persistent Storage Volumes
The local application states are perfectly synced into the container bounds mapping persistent state logs dynamically:
- `./videos:/app/videos` (Drop MP4s natively into host filesystem to process).
- `./reports:/app/reports` (CSV metrics securely bridge to the Host without data wipes).
- `./logs:/app/logs` (`drift_alert.log` propagates natively backwards).
- `./models:/app/models` (Loads the pre-compiled `honduras_dialect_binary_classifier` directly without redownloading).

## Launch Instructions
To initialize the AI ecosystem securely on any target server equipped with `docker`:
1. Navigate to the project root directory.
2. Run standard initialization binding the volume endpoints:
```bash
docker-compose up --build -d
```
3. Submit asynchronous payloads mapping to `localhost`:
```bash
curl -X POST "http://localhost:8000/validate-video" \
     -H "Content-Type: application/json" \
     -d '{"video_path": "tests/full_system/videos/vid_valid_0.mp4", "expected_topic": "Honduran people"}'
```
4. Check Model Health telemetry interacting at `http://localhost:8501`.
