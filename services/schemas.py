from pydantic import BaseModel

class VideoValidationRequest(BaseModel):
    video_path: str
    expected_topic: str

class VideoValidationResponse(BaseModel):
    transcript: str
    dialect_prediction: str
    dialect_confidence: float
    content_match_score: float
    validation_status: str


class TextValidationRequest(BaseModel):
    text: str


class TextValidationResponse(BaseModel):
    dialect_prediction: str
    dialect_confidence: float
    dialect_check: str


class AudioValidationRequest(BaseModel):
    audio_path: str


class AudioValidationResponse(BaseModel):
    transcript: str
    dialect_prediction: str
    dialect_confidence: float
    dialect_check: str


class ImageValidationRequest(BaseModel):
    image_path: str
    expected_topic: str


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
