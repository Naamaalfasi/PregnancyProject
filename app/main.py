from fastapi import FastAPI, BackgroundTasks, HTTPException
from datetime import datetime
import asyncio
import logging
from app.config import settings
from app.api import user, medical, chat, tasks
from app.database.mongo_client import mongo_client
from app.database.chroma_client import chroma_client
from app.agent.user_profile import user_profile_manager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pregnancy Agent API",
    description="Backend for proactive pregnancy companion agent",
    version="0.1.0"
)

# Include routers
app.include_router(user.router, prefix="/user-profile", tags=["User Profile"])
app.include_router(medical.router, prefix="/medical", tags=["Medical Documents"])
app.include_router(chat.router, prefix="/chat", tags=["Chat Agent"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

@app.get("/")
def root():
    return {"msg": "Pregnancy Agent API is running"}

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and schedule daily tasks"""
    try:
        await mongo_client.connect()
        await chroma_client.connect()
        
        # Schedule daily pregnancy week updates
        asyncio.create_task(schedule_daily_updates())
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await mongo_client.disconnect()
    logger.info("Application shutdown complete")

async def schedule_daily_updates():
    """Schedule daily pregnancy week updates"""
    while True:
        try:
            # Wait until 2 AM
            now = datetime.now()
            target_time = now.replace(hour=2, minute=0, second=0, microsecond=0)
            
            if now >= target_time:
                target_time = target_time.replace(day=target_time.day + 1)
            
            # Calculate seconds until target time
            seconds_until_target = (target_time - now).total_seconds()
            
            logger.info(f"Scheduling pregnancy week update for {target_time}")
            await asyncio.sleep(seconds_until_target)
            
            # Update pregnancy weeks
            updated_count = await user_profile_manager.update_all_pregnancy_weeks()
            logger.info(f"Daily pregnancy week update completed. Updated {updated_count} users.")
            
        except Exception as e:
            logger.error(f"Error in daily pregnancy week update: {e}")
            await asyncio.sleep(3600)  # Wait 1 hour before retrying

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mongo_healthy = await mongo_client.health_check()
    chroma_healthy = await chroma_client.health_check()
    
    return {
        "status": "healthy" if mongo_healthy and chroma_healthy else "unhealthy",
        "mongodb": "connected" if mongo_healthy else "disconnected",
        "chromadb": "connected" if chroma_healthy else "disconnected"
    }

@app.post("/admin/update-pregnancy-weeks")
async def manual_pregnancy_week_update(background_tasks: BackgroundTasks):
    """Manual trigger for pregnancy week updates"""
    try:
        background_tasks.add_task(user_profile_manager.update_all_pregnancy_weeks)
        return {
            "message": "Pregnancy weeks update triggered manually",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error in manual pregnancy week update: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger update")