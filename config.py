from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "shared_photos"

SESSION_TIMEOUT = timedelta(seconds=120)

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_FILE_SIZE = 15 * 1024 * 1024
MAX_FILES = 20
MAX_IMAGE_DIMENSION = 12000
MAX_IMAGE_PIXELS = 40_000_000
MAX_CONTENT_LENGTH = 100 * 1024 * 1024


def configure_app(app):
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
