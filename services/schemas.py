from pydantic import BaseModel

class VideoValidationRequest(BaseModel):
    video_path: str
    expected_topic: str
    target_country: str = "honduras"

class VideoValidationResponse(BaseModel):
    transcript: str
    dialect_prediction: str
    dialect_confidence: float
    content_match_score: float
    validation_status: str
    validation_score: float | None = None
    dialect_check: str | None = None
    detected_language: str | None = None
    expected_content: str | None = None
    geographic_verification: bool | None = None
    detected_entities: list[str] | None = None


class TextValidationRequest(BaseModel):
    text: str
    target_country: str = "honduras"


class TextValidationResponse(BaseModel):
    dialect_prediction: str
    dialect_confidence: float
    dialect_check: str


class AudioValidationRequest(BaseModel):
    audio_path: str
    target_country: str = "honduras"


class AudioValidationResponse(BaseModel):
    transcript: str
    dialect_prediction: str
    dialect_confidence: float
    dialect_check: str


class ImageValidationRequest(BaseModel):
    image_path: str
    expected_topic: str
    target_country: str = "honduras"


class ImageValidationResponse(BaseModel):
    expected_topic: str
    content_match_score: float
    validation_status: str


class AuthRegisterRequest(BaseModel):
    username: str
    password: str


class AuthLoginRequest(BaseModel):
    username: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
