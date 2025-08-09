import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "http://chroma:8000")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    ENV: str = os.getenv("ENV", "development")

settings = Settings()