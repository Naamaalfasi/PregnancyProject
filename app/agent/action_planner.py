from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from app.agent.memory_manager import memory_manager
from app.agent.user_profile import user_profile_manager
from app.utils.ai_model import ai_model

logger = logging.getLogger(__name__)

class Action:
    def __init__(self, action_type: str, description: str, priority: int = 1, 
                 metadata: Dict[str, Any] = None):
        self.action_type = action_type
        self.description = description
        self.priority = priority
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.completed = False

class ActionPlanner:
    def __init__(self):
        self.available_actions = {
            "schedule_appointment": self._schedule_appointment,
            "upload_document": self._upload_document,
            "medical_review": self._medical_review,
            "pregnancy_update": self._pregnancy_update,
            "reminder": self._create_reminder,
            "emergency_contact": self._emergency_contact,
            "pregnancy_education": self._pregnancy_education,
            "symptom_tracking": self._symptom_tracking,
            "contraction_tracking": self._contraction_tracking
        }
    
    async def analyze_user_needs(self, user_id: str, current_context: Dict[str, Any]) -> List[Action]:
        """Analyze user needs and generate appropriate actions"""
        actions = []
        
        try:
            # Get user profile
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return actions
            
            # Check pregnancy week updates
            if user_profile.pregnancy_week:
                actions.append(Action(
                    action_type="pregnancy_update",
                    description=f"Update pregnancy information for week {user_profile.pregnancy_week}",
                    priority=2,
                    metadata={"pregnancy_week": user_profile.pregnancy_week}
                ))
            
            # Check for medical review needs
            if self._needs_medical_review(user_profile, current_context):
                actions.append(Action(
                    action_type="medical_review",
                    description="Perform medical review of uploaded documents",
                    priority=1,
                    metadata={"review_type": "comprehensive"}
                ))
            
            # Check for pregnancy education needs
            if self._needs_pregnancy_education(user_profile, current_context):
                actions.append(Action(
                    action_type="pregnancy_education",
                    description=f"Provide education for pregnancy week {user_profile.pregnancy_week}",
                    priority=2,
                    metadata={"education_type": "weekly_info"}
                ))
            
            return sorted(actions, key=lambda x: x.priority, reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing user needs: {e}")
            return actions
    
    async def execute_action(self, action: Action, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action"""
        try:
            if action.action_type in self.available_actions:
                result = await self.available_actions[action.action_type](user_id, context)
                action.completed = True
                return result
            else:
                logger.warning(f"Unknown action type: {action.action_type}")
                return {"status": "error", "message": "Unknown action type"}
                
        except Exception as e:
            logger.error(f"Error executing action {action.action_type}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _medical_review(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform medical review using AI model"""
        try:
            documents = await user_profile_manager.get_user_medical_documents(user_id)
            
            if not documents:
                return {
                    "status": "info",
                    "message": "No medical documents found for review",
                    "action_type": "medical_review"
                }
            
            # Prepare context for AI model
            review_context = {
                "user_id": user_id,
                "documents": [doc.dict() for doc in documents],
                "context": context,
                "review_type": "comprehensive"
            }
            
            # Get AI review
            ai_review = await ai_model.generate_medical_review(review_context)
            
            # Store medical review memory
            await memory_manager.store_medical_memory(
                user_id=user_id,
                document_type="review",
                content=f"Medical review completed: {ai_review.get('summary', '')}",
                importance=0.9
            )
            
            return {
                "status": "success",
                "message": "Medical review completed",
                "review_results": ai_review,
                "action_type": "medical_review"
            }
            
        except Exception as e:
            logger.error(f"Error in medical review: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _pregnancy_update(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update pregnancy information"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if user_profile and user_profile.lmp_date:
                current_week = await user_profile_manager.calculate_pregnancy_week(user_profile.lmp_date)
                
                if current_week != user_profile.pregnancy_week:
                    await user_profile_manager.update_user_profile(user_id, {"pregnancy_week": current_week})
                    
                    # Get AI insights for the new week
                    week_insights = await ai_model.generate_pregnancy_week_insights(
                        user_id=user_id,
                        week=current_week,
                        context=context
                    )
                    
                    await memory_manager.store_pregnancy_memory(
                        user_id=user_id,
                        week=current_week,
                        content=f"Pregnancy week updated to {current_week}. Insights: {week_insights.get('summary', '')}",
                        importance=0.8
                    )
                    
                    return {
                        "status": "success",
                        "message": f"Pregnancy week updated to {current_week}",
                        "pregnancy_week": current_week,
                        "insights": week_insights,
                        "action_type": "pregnancy_update"
                    }
            
            return {
                "status": "info",
                "message": "Pregnancy week is up to date",
                "action_type": "pregnancy_update"
            }
            
        except Exception as e:
            logger.error(f"Error in pregnancy update: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _pregnancy_education(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide pregnancy education using AI"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            week = user_profile.pregnancy_week if user_profile else None
            
            if week:
                # Get AI-generated education content
                education_content = await ai_model.generate_pregnancy_education(
                    user_id=user_id,
                    week=week,
                    context=context
                )
                
                await memory_manager.store_pregnancy_memory(
                    user_id=user_id,
                    week=week,
                    content=f"Provided AI-generated education for week {week}",
                    importance=0.6
                )
                
                return {
                    "status": "success",
                    "message": f"Pregnancy education for week {week}",
                    "action_type": "pregnancy_education",
                    "week": week,
                    "content": education_content
                }
            
            return {
                "status": "info",
                "message": "Pregnancy week information needed for education",
                "action_type": "pregnancy_education"
            }
            
        except Exception as e:
            logger.error(f"Error in pregnancy education: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _contraction_tracking(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Track contractions using AI analysis"""
        try:
            contraction_data = context.get("contraction_data", {})
            if contraction_data:
                # Get AI analysis of contractions
                ai_analysis = await ai_model.analyze_contractions(
                    user_id=user_id,
                    contraction_data=contraction_data,
                    context=context
                )
                
                await memory_manager.store_pregnancy_memory(
                    user_id=user_id,
                    week=0,
                    content=f"AI contraction analysis: {ai_analysis.get('summary', '')}",
                    importance=0.9
                )
                
                return {
                    "status": "success",
                    "message": "Contraction analysis completed",
                    "action_type": "contraction_tracking",
                    "analysis": ai_analysis
                }
            
            return {
                "status": "info",
                "message": "Contraction data needed for analysis",
                "action_type": "contraction_tracking"
            }
            
        except Exception as e:
            logger.error(f"Error in contraction tracking: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _schedule_appointment(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an appointment with AI assistance"""
        try:
            appointment_type = context.get("appointment_type", "general")
            
            # Get AI recommendations for appointment scheduling
            ai_recommendations = await ai_model.generate_appointment_recommendations(
                user_id=user_id,
                appointment_type=appointment_type,
                context=context
            )
            
            await memory_manager.store_memory(
                user_id=user_id,
                memory_type="appointment",
                content=f"AI-assisted appointment scheduling for {appointment_type}",
                importance=0.8
            )
            
            return {
                "status": "success",
                "message": f"Appointment scheduling for {appointment_type} with AI recommendations",
                "action_type": "schedule_appointment",
                "appointment_type": appointment_type,
                "recommendations": ai_recommendations
            }
        except Exception as e:
            logger.error(f"Error in appointment scheduling: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _upload_document(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document upload with AI analysis"""
        try:
            document_types = context.get("document_types", ["general"])
            
            # Get AI recommendations for document upload
            ai_recommendations = await ai_model.generate_document_upload_recommendations(
                user_id=user_id,
                document_types=document_types,
                context=context
            )
            
            return {
                "status": "success",
                "message": f"Document upload available with AI recommendations",
                "action_type": "upload_document",
                "document_types": document_types,
                "recommendations": ai_recommendations
            }
        except Exception as e:
            logger.error(f"Error in document upload: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _create_reminder(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reminder with AI optimization"""
        try:
            reminder_type = context.get("reminder_type", "general")
            
            # Get AI-optimized reminder settings
            ai_reminder = await ai_model.generate_reminder_settings(
                user_id=user_id,
                reminder_type=reminder_type,
                context=context
            )
            
            await memory_manager.store_memory(
                user_id=user_id,
                memory_type="reminder",
                content=f"AI-optimized reminder created for {reminder_type}",
                importance=0.7
            )
            
            return {
                "status": "success",
                "message": f"AI-optimized reminder created for {reminder_type}",
                "action_type": "reminder",
                "reminder_type": reminder_type,
                "settings": ai_reminder
            }
        except Exception as e:
            logger.error(f"Error in reminder creation: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _emergency_contact(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency contact with AI assistance"""
        try:
            user_profile = await user_profile_manager.get_user_profile(user_id)
            emergency_contact = user_profile.emergency_contact if user_profile else None
            
            # Get AI emergency recommendations
            ai_emergency = await ai_model.generate_emergency_recommendations(
                user_id=user_id,
                emergency_contact=emergency_contact,
                context=context
            )
            
            return {
                "status": "success",
                "message": "Emergency contact information with AI recommendations",
                "action_type": "emergency_contact",
                "emergency_contact": emergency_contact,
                "recommendations": ai_emergency
            }
        except Exception as e:
            logger.error(f"Error in emergency contact: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _symptom_tracking(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Track symptoms with AI analysis"""
        try:
            tracking_type = context.get("tracking_type", "daily")
            
            # Get AI symptom analysis
            ai_symptom_analysis = await ai_model.analyze_symptoms(
                user_id=user_id,
                tracking_type=tracking_type,
                context=context
            )
            
            await memory_manager.store_pregnancy_memory(
                user_id=user_id,
                week=0,
                content=f"AI symptom analysis for {tracking_type} tracking",
                importance=0.7
            )
            
            return {
                "status": "success",
                "message": f"AI symptom tracking ({tracking_type}) initiated",
                "action_type": "symptom_tracking",
                "tracking_type": tracking_type,
                "analysis": ai_symptom_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in symptom tracking: {e}")
            return {"status": "error", "message": str(e)}
    
    def _needs_medical_review(self, user_profile, context: Dict[str, Any]) -> bool:
        """Check if user needs medical review"""
        return len(user_profile.medical_documents) > 0
    
    def _needs_pregnancy_education(self, user_profile, context: Dict[str, Any]) -> bool:
        """Check if user needs pregnancy education"""
        return user_profile and user_profile.pregnancy_week and user_profile.pregnancy_week > 0

# Global instance
action_planner = ActionPlanner()