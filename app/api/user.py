from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.agent.user_profile import UserProfile, UserProfileUpdate, user_profile_manager
from app.database.mongo_client import mongo_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile by user_id"""
    try:
        profile = await user_profile_manager.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get pregnancy info
        pregnancy_info = await user_profile_manager.get_pregnancy_info(user_id)
        
        # Get document summary
        document_summary = await user_profile_manager.get_document_summary(user_id)
        
        return {
            "profile": profile.dict(),
            "pregnancy_info": pregnancy_info,
            "document_summary": document_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/{user_id}")
async def update_user_profile(user_id: str, profile_update: UserProfileUpdate):
    """Update user profile"""
    try:
        # Check if user exists
        existing_profile = await user_profile_manager.get_user_profile(user_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Update profile
        update_data = profile_update.dict(exclude_unset=True)
        updated_profile = await user_profile_manager.update_user_profile(user_id, update_data)
        
        if not updated_profile:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        # Get updated pregnancy info
        pregnancy_info = await user_profile_manager.get_pregnancy_info(user_id)
        
        # Get updated document summary
        document_summary = await user_profile_manager.get_document_summary(user_id)
        
        return {
            "message": "Profile updated successfully",
            "profile": updated_profile.dict(),
            "pregnancy_info": pregnancy_info,
            "document_summary": document_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{user_id}")
async def create_user_profile(user_id: str, profile: UserProfile):
    """Create new user profile"""
    try:
        # Check if user already exists
        existing_profile = await user_profile_manager.get_user_profile(user_id)
        if existing_profile:
            raise HTTPException(status_code=409, detail="User profile already exists")
        
        # Create new profile
        profile_data = profile.dict(exclude={"user_id", "created_at", "updated_at", "medical_documents"})
        new_profile = await user_profile_manager.create_user_profile(user_id, profile_data)
        
        return {
            "message": "User profile created successfully",
            "profile": new_profile.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}/pregnancy-info")
async def get_pregnancy_info(user_id: str):
    """Get pregnancy-specific information"""
    try:
        pregnancy_info = await user_profile_manager.get_pregnancy_info(user_id)
        if not pregnancy_info:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return pregnancy_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pregnancy info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}/documents")
async def get_user_documents(user_id: str):
    """Get all medical documents for user"""
    try:
        documents = await user_profile_manager.get_user_medical_documents(user_id)
        summary = await user_profile_manager.get_document_summary(user_id)
        
        return {
            "user_id": user_id,
            "documents": [doc.dict() for doc in documents],
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting user documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")