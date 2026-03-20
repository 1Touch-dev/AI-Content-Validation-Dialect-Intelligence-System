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
