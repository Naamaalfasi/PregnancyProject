from fastapi import FastAPI
from app.config import settings
from app.api import user

app = FastAPI(
    title="Pregnancy Agent API",
    description="Backend for proactive pregnancy companion agent",
    version="0.1.0"
)

app.include_router(user.router, prefix="/user-profile", tags=["User Profile"])

@app.get("/")
def root():
    return {"msg": "Pregnancy Agent API is running"}