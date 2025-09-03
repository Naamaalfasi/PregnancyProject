import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "http://chroma:8000")
    ENV: str = os.getenv("ENV", "development")

settings = Settings()