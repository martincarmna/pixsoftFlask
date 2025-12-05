import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "supersecreto123"
    DATABASE = os.path.join(BASE_DIR, "database.db")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/imagenes")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
