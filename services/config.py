import os

BASE_DIR = os.getenv("BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DEFAULT_DIALECT_MODEL_PATH = os.path.join(MODELS_DIR, "honduras_dialect_binary_classifier")
DIALECT_MODEL_PATH = os.getenv("MODEL_PATH", DEFAULT_DIALECT_MODEL_PATH)
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Thresholds
VALIDATION_THRESHOLD = 0.70
