from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from app.agent.user_profile import user_profile_manager
from app.agent.memory_manager import memory_manager
from app.utils.ai_model import ai_model

logger = logging.getLogger(__name__)

class TimelineManager:
    def __init__(self):
        self.pregnancy_milestones = {
            4: "תאריך הווסת האחרונה",
            8: "דופק עובר ראשון",
            12: "בדיקת שקיפות עורפית",
            16: "בדיקת מין העובר",
            20: "אולטרסאונד מורפולוגי",
            24: "בדיקת סוכר בהריון",
            28: "חיסון טטנוס-דיפטריה",
            32: "בדיקת גדילה",
            36: "בדיקת GBS",
            38: "הכנה ללידה",
            40: "תאריך לידה צפוי"
        }
    
    async def get_pregnancy_timeline(self, user_id: str) -> Dict[str, Any]:
        """Get pregnancy timeline for user"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            current_week = user_profile.pregnancy_week or 0
            lmp_date = user_profile.lmp_date
            
            # Calculate timeline
            timeline = await self._calculate_timeline(current_week, lmp_date)
            
            # Get AI insights for timeline
            ai_insights = await ai_model.generate_timeline_insights(
                user_id=user_id,
                current_week=current_week,
                timeline=timeline
            )
            
            return {
                "user_id": user_id,
                "current_week": current_week,
                "lmp_date": lmp_date.isoformat() if lmp_date else None,
                "timeline": timeline,
                "ai_insights": ai_insights,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting pregnancy timeline: {e}")
            return {"error": "Failed to get timeline"}
    
    async def _calculate_timeline(self, current_week: int, lmp_date: Optional[datetime]) -> List[Dict[str, Any]]:
        """Calculate pregnancy timeline"""
        timeline = []
        
        if not lmp_date:
            return timeline
        
        # Calculate dates for each week
        for week in range(1, 41):
            week_date = lmp_date + timedelta(weeks=week)
            
            milestone_info = {
                "week": week,
                "date": week_date.isoformat(),
                "milestone": self.pregnancy_milestones.get(week, f"שבוע {week} להריון"),
                "status": "completed" if week < current_week else "current" if week == current_week else "upcoming",
                "days_until": (week_date - datetime.utcnow()).days if week >= current_week else None
            }
            
            timeline.append(milestone_info)
        
        return timeline
    
    async def get_week_details(self, user_id: str, week: int) -> Dict[str, Any]:
        """Get detailed information for a specific week"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            # Get AI insights for the specific week
            week_insights = await ai_model.generate_pregnancy_week_insights(
                user_id=user_id,
                week=week,
                context={"detailed_analysis": True}
            )
            
            # Get milestone information
            milestone = self.pregnancy_milestones.get(week, f"שבוע {week} להריון")
            
            # Calculate week date
            week_date = None
            if user_profile.lmp_date:
                week_date = user_profile.lmp_date + timedelta(weeks=week)
            
            return {
                "user_id": user_id,
                "week": week,
                "milestone": milestone,
                "date": week_date.isoformat() if week_date else None,
                "insights": week_insights,
                "trimester": self._get_trimester(week),
                "development_stage": self._get_development_stage(week)
            }
            
        except Exception as e:
            logger.error(f"Error getting week details: {e}")
            return {"error": "Failed to get week details"}
    
    def _get_trimester(self, week: int) -> str:
        """Get trimester for a given week"""
        if week <= 13:
            return "ראשון"
        elif week <= 26:
            return "שני"
        else:
            return "שלישי"
    
    def _get_development_stage(self, week: int) -> str:
        """Get development stage for a given week"""
        if week <= 12:
            return "עובר"
        else:
            return "עובר מתפתח"
    
    async def get_upcoming_milestones(self, user_id: str, weeks_ahead: int = 4) -> List[Dict[str, Any]]:
        """Get upcoming milestones for the next few weeks"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return []
            
            current_week = user_profile.pregnancy_week or 0
            upcoming_milestones = []
            
            for week in range(current_week + 1, min(current_week + weeks_ahead + 1, 41)):
                if week in self.pregnancy_milestones:
                    milestone_info = await self.get_week_details(user_id, week)
                    upcoming_milestones.append(milestone_info)
            
            return upcoming_milestones
            
        except Exception as e:
            logger.error(f"Error getting upcoming milestones: {e}")
            return []
    
    async def get_completed_milestones(self, user_id: str) -> List[Dict[str, Any]]:
        """Get completed milestones for user"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return []
            
            current_week = user_profile.pregnancy_week or 0
            completed_milestones = []
            
            for week in range(1, current_week + 1):
                if week in self.pregnancy_milestones:
                    milestone_info = await self.get_week_details(user_id, week)
                    completed_milestones.append(milestone_info)
            
            return completed_milestones
            
        except Exception as e:
            logger.error(f"Error getting completed milestones: {e}")
            return []
    
    async def update_pregnancy_progress(self, user_id: str) -> Dict[str, Any]:
        """Update pregnancy progress and trigger notifications"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            # Calculate current week
            if user_profile.lmp_date:
                current_week = await user_profile_manager.calculate_pregnancy_week(user_profile.lmp_date)
                
                if current_week != user_profile.pregnancy_week:
                    # Update user profile
                    await user_profile_manager.update_user_profile(user_id, {"pregnancy_week": current_week})
                    
                    # Generate AI insights for the new week
                    week_insights = await ai_model.generate_pregnancy_week_insights(
                        user_id=user_id,
                        week=current_week,
                        context={"progress_update": True}
                    )
                    
                    # Store memory about progress update
                    await memory_manager.store_pregnancy_memory(
                        user_id=user_id,
                        week=current_week,
                        content=f"Pregnancy progress updated to week {current_week}",
                        importance=0.8
                    )
                    
                    return {
                        "user_id": user_id,
                        "previous_week": user_profile.pregnancy_week,
                        "current_week": current_week,
                        "week_insights": week_insights,
                        "milestone": self.pregnancy_milestones.get(current_week, f"שבוע {current_week} להריון")
                    }
            
            return {
                "user_id": user_id,
                "current_week": user_profile.pregnancy_week,
                "message": "No progress update needed"
            }
            
        except Exception as e:
            logger.error(f"Error updating pregnancy progress: {e}")
            return {"error": "Failed to update progress"}
    
    async def get_pregnancy_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive pregnancy summary"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return {"error": "User profile not found"}
            
            current_week = user_profile.pregnancy_week or 0
            
            # Get timeline
            timeline = await self.get_pregnancy_timeline(user_id)
            
            # Get completed and upcoming milestones
            completed_milestones = await self.get_completed_milestones(user_id)
            upcoming_milestones = await self.get_upcoming_milestones(user_id)
            
            # Get AI summary
            ai_summary = await ai_model.generate_pregnancy_summary(
                user_id=user_id,
                current_week=current_week,
                completed_milestones=completed_milestones,
                upcoming_milestones=upcoming_milestones
            )
            
            return {
                "user_id": user_id,
                "current_week": current_week,
                "trimester": self._get_trimester(current_week),
                "completed_milestones": completed_milestones,
                "upcoming_milestones": upcoming_milestones,
                "ai_summary": ai_summary,
                "progress_percentage": (current_week / 40) * 100,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting pregnancy summary: {e}")
            return {"error": "Failed to get pregnancy summary"}

# Global instance
timeline_manager = TimelineManager()
