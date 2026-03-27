import os
import sys
import tempfile
import shutil
import torch
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, Header

# Ensure parent path for VideoValidator resolution natively
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from services.schemas import (
    VideoValidationRequest,
    VideoValidationResponse,
    TextValidationRequest,
    TextValidationResponse,
    AudioValidationRequest,
    AudioValidationResponse,
    ImageValidationRequest,
    ImageValidationResponse,
    AuthRegisterRequest,
    AuthLoginRequest,
    AuthTokenResponse,
)
from services.config import VALIDATION_THRESHOLD
from services.auth_store import (
    create_user,
    authenticate_user,
    create_session,
    get_session,
    revoke_session,
)

# Load the heavy ML model uniquely into app state during startup
from video_validator import VideoValidator
import uvicorn

app = FastAPI(title="Video Validation Service")
validator_cache = {}
SUPPORTED_COUNTRIES = {"honduras", "ecuador"}

frontend_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _extract_bearer_token(auth_header: str) -> str:
    if not auth_header:
        return ""
    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return ""
    return parts[1].strip()


def require_auth(authorization: str = Header(default="")) -> dict:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token.")
    session = get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return session


def _ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "FFmpeg is not available in PATH. Install FFmpeg and ensure "
                "`ffmpeg` is reachable from terminal."
            ),
        )


def _normalize_country(country: str) -> str:
    value = (country or "honduras").strip().lower()
    if value not in SUPPORTED_COUNTRIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target_country '{country}'. Supported: {sorted(SUPPORTED_COUNTRIES)}",
        )
    return value


def _get_validator(country: str) -> VideoValidator:
    normalized = _normalize_country(country)
    if normalized not in validator_cache:
        validator_cache[normalized] = VideoValidator(country=normalized)
    return validator_cache[normalized]


def _transcribe_audio_to_text(validator: VideoValidator, audio_path: str) -> str:
    """
    Normalize Whisper output shape across engines.
    - faster-whisper: (segments, info)
    - openai-whisper style: {"text": "..."}
    """
    result = validator.whisper_model.transcribe(audio_path, language="es")

    if isinstance(result, tuple) and len(result) >= 1:
        segments = result[0]
        transcript_parts = [segment.text for segment in segments if getattr(segment, "text", "").strip()]
        return " ".join(transcript_parts).strip()

    if isinstance(result, dict):
        return (result.get("text") or "").strip()

    return ""


def _validate_image_core(
    image: Image.Image,
    image_path_for_ocr: str,
    expected_topic: str,
    validator: VideoValidator,
) -> ImageValidationResponse:
    ocr_results = validator.ocr_reader.readtext(image_path_for_ocr, detail=0)
    text_embedded = " ".join(ocr_results).lower()
    for blocked in validator.config.get("ocr_blacklist", []):
        if blocked in text_embedded:
            return ImageValidationResponse(
                expected_topic=expected_topic,
                content_match_score=0.0,
                validation_status="FAIL",
            )

    target_list = [
        expected_topic,
        "Ecuador scenery or people",
        "Mexico scenery or people",
        "Generic unbranded people or background",
    ]
    inputs = validator.clip_processor(
        text=target_list,
        images=image,
        return_tensors="pt",
        padding=True,
    )
    for key, value in inputs.items():
        if hasattr(value, "to"):
            inputs[key] = value.to(validator.device)

    with torch.no_grad():
        outputs = validator.clip_model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)
    score = round(probs[:, 0].mean().item(), 4)

    return ImageValidationResponse(
        expected_topic=expected_topic,
        content_match_score=score,
        validation_status="PASS" if score >= VALIDATION_THRESHOLD else "FAIL",
    )

@app.on_event("startup")
def startup_event():
    # Warm up default country model to reduce first request latency.
    _get_validator("honduras")


@app.post("/auth/register")
def auth_register(request: AuthRegisterRequest):
    username = (request.username or "").strip()
    password = request.password or ""

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    ok, message = create_user(username=username, password=password)
    if not ok:
        raise HTTPException(status_code=409, detail=message)
    return {"ok": True, "message": "Registration successful."}


@app.post("/auth/login", response_model=AuthTokenResponse)
def auth_login(request: AuthLoginRequest):
    username = (request.username or "").strip()
    password = request.password or ""
    user = authenticate_user(username=username, password=password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_session(user_id=user["id"], username=user["username"])
    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        username=user["username"],
    )


@app.post("/auth/logout")
def auth_logout(session=Depends(require_auth), authorization: str = Header(default="")):
    token = _extract_bearer_token(authorization)
    revoke_session(token)
    return {"ok": True, "message": "Logged out successfully."}


@app.get("/auth/me")
def auth_me(session=Depends(require_auth)):
    return {
        "ok": True,
        "user": {
            "id": session.get("user_id"),
            "username": session.get("username"),
        },
    }


@app.post("/validate-video", response_model=VideoValidationResponse)
def validate_video(request: VideoValidationRequest, session=Depends(require_auth)):
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=400, detail="Video file not found.")

    try:
        validator = _get_validator(request.target_country)
        result = validator.validate_video(request.video_path, expected_content=request.expected_topic)
        if not result:
            raise HTTPException(status_code=500, detail="Validation failed internally.")

        result["dialect_prediction"] = result.pop("dialect_predicted", "Other")
        return VideoValidationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-text", response_model=TextValidationResponse)
def validate_text(request: TextValidationRequest, session=Depends(require_auth)):
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        validator = _get_validator(request.target_country)
        res = validator.dialect_classifier(text)[0]
        prediction = res["label"]
        confidence = round(res["score"], 4)
        return TextValidationResponse(
            dialect_prediction=prediction,
            dialect_confidence=confidence,
            dialect_check="pass" if prediction == validator.config["label"] else "fail",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-audio", response_model=AudioValidationResponse)
def validate_audio(request: AudioValidationRequest, session=Depends(require_auth)):
    _ensure_ffmpeg_available()
    if not os.path.exists(request.audio_path):
        raise HTTPException(status_code=400, detail="Audio file not found.")

    try:
        validator = _get_validator(request.target_country)
        transcript = _transcribe_audio_to_text(validator, request.audio_path)

        prediction = "Other"
        confidence = 0.0
        if transcript:
            cls = validator.dialect_classifier(transcript)[0]
            prediction = cls["label"]
            confidence = round(cls["score"], 4)

        return AudioValidationResponse(
            transcript=transcript,
            dialect_prediction=prediction,
            dialect_confidence=confidence,
            dialect_check="pass" if prediction == validator.config["label"] else "fail",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-audio-upload", response_model=AudioValidationResponse)
async def validate_audio_upload(
    audio: UploadFile = File(...),
    target_country: str = Form("honduras"),
    session=Depends(require_auth),
):
    _ensure_ffmpeg_available()
    suffix = os.path.splitext(audio.filename or "")[1] or ".wav"
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=suffix).name
    try:
        validator = _get_validator(target_country)
        content = await audio.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded audio is empty.")
        with open(temp_path, "wb") as f:
            f.write(content)

        transcript = _transcribe_audio_to_text(validator, temp_path)

        prediction = "Other"
        confidence = 0.0
        if transcript:
            cls = validator.dialect_classifier(transcript)[0]
            prediction = cls["label"]
            confidence = round(cls["score"], 4)

        return AudioValidationResponse(
            transcript=transcript,
            dialect_prediction=prediction,
            dialect_confidence=confidence,
            dialect_check="pass" if prediction == validator.config["label"] else "fail",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@app.post("/validate-image", response_model=ImageValidationResponse)
def validate_image(request: ImageValidationRequest, session=Depends(require_auth)):
    if not os.path.exists(request.image_path):
        raise HTTPException(status_code=400, detail="Image file not found.")

    try:
        validator = _get_validator(request.target_country)
        image = Image.open(request.image_path).convert("RGB")
        return _validate_image_core(
            image=image,
            image_path_for_ocr=request.image_path,
            expected_topic=request.expected_topic,
            validator=validator,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-image-upload", response_model=ImageValidationResponse)
async def validate_image_upload(
    expected_topic: str = Form(...),
    image: UploadFile = File(...),
    target_country: str = Form("honduras"),
    session=Depends(require_auth),
):
    suffix = os.path.splitext(image.filename or "")[1] or ".jpg"
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=suffix).name
    try:
        validator = _get_validator(target_country)
        content = await image.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")
        with open(temp_path, "wb") as f:
            f.write(content)

        pil_image = Image.open(temp_path).convert("RGB")
        return _validate_image_core(
            image=pil_image,
            image_path_for_ocr=temp_path,
            expected_topic=expected_topic,
            validator=validator,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@app.post("/validate-video-upload", response_model=VideoValidationResponse)
async def validate_video_upload(
    expected_topic: str = Form(...),
    video: UploadFile = File(...),
    target_country: str = Form("honduras"),
    session=Depends(require_auth),
):
    _ensure_ffmpeg_available()
    suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=suffix).name
    try:
        validator = _get_validator(target_country)
        content = await video.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded video is empty.")
        with open(temp_path, "wb") as f:
            f.write(content)

        result = validator.validate_video(temp_path, expected_content=expected_topic)
        if not result:
            raise HTTPException(status_code=500, detail="Validation failed internally.")
        result["dialect_prediction"] = result.pop("dialect_predicted", "Other")
        return VideoValidationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

if __name__ == "__main__":
    uvicorn.run("services.api_server:app", host="0.0.0.0", port=8000, reload=False)
