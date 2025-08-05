from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
from app.agent.memory_manager import memory_manager
from app.agent.action_planner import action_planner
from app.agent.user_profile import user_profile_manager
from app.utils.ai_model import ai_model

logger = logging.getLogger(__name__)

class ChatRouter:
    def __init__(self):
        self.conversation_contexts = {}
    
    async def process_message(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user message and generate a response"""
        try:
            # Get user profile
            user_profile = await user_profile_manager.get_user_profile(user_id)
            if not user_profile:
                return {
                    "response": "אני לא מכיר אותך עדיין. אנא צור פרופיל משתמש תחילה.",
                    "actions": [],
                    "context": {},
                    "needs_profile": True
                }
            
            # Get conversation context
            conversation_context = await self._get_conversation_context(user_id, context)
            
            # Analyze user needs
            actions = await action_planner.analyze_user_needs(user_id, conversation_context)
            
            # Generate response based on message content and context
            response = await self._generate_response(user_id, message, user_profile, conversation_context, actions)
            
            # Store conversation
            await memory_manager.store_conversation(user_id, message, response, conversation_context)
            
            # Execute high-priority actions
            executed_actions = []
            for action in actions[:3]:  # Execute top 3 actions
                if action.priority >= 2:
                    result = await action_planner.execute_action(action, user_id, conversation_context)
                    executed_actions.append({
                        "action_type": action.action_type,
                        "description": action.description,
                        "result": result
                    })
            
            return {
                "response": response,
                "actions": executed_actions,
                "context": conversation_context,
                "user_profile": user_profile.dict() if user_profile else None,
                "needs_profile": False
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "מצטערת, נתקלתי בשגיאה בעיבוד ההודעה שלך. אנא נסה שוב.",
                "actions": [],
                "context": {},
                "needs_profile": False
            }
    
    async def _get_conversation_context(self, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get conversation context for the user"""
        try:
            # Get recent conversations
            recent_conversations = await memory_manager.get_recent_conversations(user_id, limit=5)
            
            # Get relevant memories
            relevant_memories = await memory_manager.get_relevant_memories(user_id, "", limit=3)
            
            # Get user profile
            user_profile = await user_profile_manager.get_user_profile(user_id)
            
            # Get medical documents
            medical_documents = await user_profile_manager.get_user_medical_documents(user_id)
            
            conversation_context = {
                "recent_conversations": recent_conversations,
                "relevant_memories": relevant_memories,
                "user_profile": user_profile.dict() if user_profile else None,
                "medical_documents": [doc.dict() for doc in medical_documents] if medical_documents else [],
                "current_time": datetime.utcnow().isoformat(),
                "context": context or {}
            }
            
            return conversation_context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {}
    
    async def _generate_response(self, user_id: str, message: str, user_profile, 
                               conversation_context: Dict[str, Any], actions: List) -> str:
        """Generate a response based on the message and context"""
        try:
            # Check for specific intents
            intent = self._detect_intent(message)
            
            if intent == "greeting":
                return self._generate_greeting(user_profile)
            elif intent == "pregnancy_info":
                return await self._generate_pregnancy_info(user_profile)
            elif intent == "medical_documents":
                return await self._generate_medical_documents_info(user_id)
            elif intent == "medical_review":
                return await self._generate_medical_review_response(user_id, message)
            elif intent == "appointment":
                return self._generate_appointment_response()
            elif intent == "emergency":
                return self._generate_emergency_response(user_profile)
            elif intent == "contraction_tracking":
                return await self._generate_contraction_tracking_response(user_id, message)
            elif intent == "pregnancy_week_check":
                return await self._generate_pregnancy_week_check(user_profile)
            else:
                return self._generate_general_response(message, actions)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "אני כאן כדי לעזור לך במסע ההריון שלך. איך אוכל לסייע לך היום?"
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent of the user message"""
        message_lower = message.lower()
        
        # Greeting patterns
        if any(word in message_lower for word in ["שלום", "היי", "הי", "בוקר טוב", "ערב טוב", "hello", "hi", "hey"]):
            return "greeting"
        
        # Pregnancy info patterns
        elif any(word in message_lower for word in ["הריון", "שבוע", "תאריך לידה", "עובר", "pregnancy", "week", "due date"]):
            return "pregnancy_info"
        
        # Medical documents patterns
        elif any(word in message_lower for word in ["מסמך", "העלאה", "רפואי", "בדיקה", "ultrasound", "blood test", "document"]):
            return "medical_documents"
        
        # Medical review patterns
        elif any(word in message_lower for word in ["חוות דעת", "סקירה", "בדיקה", "תוצאות", "review", "opinion", "results"]):
            return "medical_review"
        
        # Appointment patterns
        elif any(word in message_lower for word in ["תור", "ביקור", "רופא", "appointment", "visit", "doctor"]):
            return "appointment"
        
        # Emergency patterns
        elif any(word in message_lower for word in ["חירום", "דחוף", "עזרה", "emergency", "urgent", "help"]):
            return "emergency"
        
        # Contraction tracking patterns
        elif any(word in message_lower for word in ["צירים", "contractions", "ציר", "contraction"]):
            return "contraction_tracking"
        
        # Pregnancy week check patterns
        elif any(word in message_lower for word in ["בדיקה", "ביצעת", "קנית", "test", "did you", "bought"]):
            return "pregnancy_week_check"
        
        else:
            return "general"
    
    def _generate_greeting(self, user_profile) -> str:
        """Generate a greeting response"""
        if user_profile and user_profile.name:
            return f"שלום {user_profile.name}! אני הסוכן שלך למעקב הריון. איך את מרגישה היום?"
        else:
            return "שלום! אני הסוכן שלך למעקב הריון. איך אוכל לעזור לך היום?"
    
    async def _generate_pregnancy_info(self, user_profile) -> str:
        """Generate pregnancy information response"""
        if not user_profile:
            return "אני לא מכיר את פרטי ההריון שלך עדיין. אנא עדכן את הפרופיל עם תאריך הלידה הצפוי או תאריך הווסת האחרונה."
        
        if user_profile.pregnancy_week:
            trimester = "ראשון" if user_profile.pregnancy_week <= 13 else "שני" if user_profile.pregnancy_week <= 26 else "שלישי"
            return f"את נמצאת בשבוע {user_profile.pregnancy_week} להריון (טרימסטר {trimester}). זה זמן מרגש! האם יש משהו ספציפי שתרצי לדעת על השבוע הזה?"
        else:
            return "אני לא מכיר את שבוע ההריון הנוכחי שלך. אנא עדכן את הפרופיל עם תאריך הלידה הצפוי או תאריך הווסת האחרונה."
    
    async def _generate_medical_documents_info(self, user_id: str) -> str:
        """Generate medical documents information"""
        try:
            documents = await user_profile_manager.get_user_medical_documents(user_id)
            
            if not documents:
                return "עדיין לא העלית מסמכים רפואיים. את יכולה להעלות בדיקות דם, אולטרסאונד, הערות רופא ומרשמים דרך מדור המסמכים הרפואיים."
            
            doc_types = {}
            for doc in documents:
                doc_types[doc.doc_type] = doc_types.get(doc.doc_type, 0) + 1
            
            doc_summary = ", ".join([f"{count} {doc_type}" for doc_type, count in doc_types.items()])
            return f"העלית {len(documents)} מסמכים רפואיים: {doc_summary}. האם תרצי שאסקור אותם עבורך?"
            
        except Exception as e:
            logger.error(f"Error getting medical documents info: {e}")
            return "יש לי בעיה לגשת למסמכים הרפואיים שלך כרגע. אנא נסה שוב מאוחר יותר."
    
    async def _generate_medical_review_response(self, user_id: str, message: str) -> str:
        """Generate medical review response"""
        try:
            documents = await user_profile_manager.get_user_medical_documents(user_id)
            
            if not documents:
                return "אין לך מסמכים רפואיים לסקירה. אנא העלה מסמכים תחילה."
            
            # Use AI model for medical review
            review_context = {
                "user_id": user_id,
                "documents": [doc.dict() for doc in documents],
                "message": message
            }
            
            ai_review = await ai_model.generate_medical_review(review_context)
            
            return f"סקירה רפואית: {ai_review.get('summary', 'המסמכים נבדקו')}. {ai_review.get('recommendations', 'המשך מעקב שגרתי')}"
                
        except Exception as e:
            logger.error(f"Error generating medical review: {e}")
            return "יש לי בעיה ליצור סקירה רפואית כרגע. אנא נסה שוב מאוחר יותר."
    
    async def _generate_contraction_tracking_response(self, user_id: str, message: str) -> str:
        """Generate contraction tracking response"""
        try:
            # Extract contraction information from message
            contraction_info = self._extract_contraction_info(message)
            
            if contraction_info:
                # Use AI model for contraction analysis
                ai_analysis = await ai_model.analyze_contractions(
                    user_id=user_id,
                    contraction_data=contraction_info,
                    context={"message": message}
                )
                
                return f"ניתוח צירים: {ai_analysis.get('pattern', 'דפוס תקין')}. {ai_analysis.get('recommendation', 'המשך מעקב')}"
            else:
                return "אני יכול לעזור לך לעקוב אחר הצירים. אנא ספרי לי:\n- כמה זמן נמשך כל ציר?\n- מה המרווח בין הצירים?\n- מתי התחילו?"
                
        except Exception as e:
            logger.error(f"Error in contraction tracking: {e}")
            return "יש לי בעיה לעקוב אחר הצירים כרגע. אנא נסה שוב."
    
    def _extract_contraction_info(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract contraction information from message"""
        # This is a simplified version - in reality, you'd use NLP
        contraction_info = {}
        
        # Look for duration patterns
        duration_patterns = [
            r'(\d+)\s*דקות?',
            r'(\d+)\s*minutes?'
        ]
        
        import re
        for pattern in duration_patterns:
            match = re.search(pattern, message)
            if match:
                contraction_info["duration"] = int(match.group(1))
                break
        
        # Look for interval patterns
        interval_patterns = [
            r'מרווח\s*(\d+)\s*דקות?',
            r'interval\s*(\d+)\s*minutes?'
        ]
        
        for pattern in interval_patterns:
            match = re.search(pattern, message)
            if match:
                contraction_info["interval"] = int(match.group(1))
                break
        
        return contraction_info if contraction_info else None
    
    async def _generate_pregnancy_week_check(self, user_profile) -> str:
        """Generate pregnancy week check response"""
        if not user_profile or not user_profile.pregnancy_week:
            return "אני לא מכיר את שבוע ההריון שלך. אנא עדכן את הפרופיל."
        
        week = user_profile.pregnancy_week
        
        # Use AI model for week-specific insights
        week_insights = await ai_model.generate_pregnancy_week_insights(
            user_id=user_profile.user_id,
            week=week,
            context={"check_type": "weekly_check"}
        )
        
        return f"בשבוע {week} להריון: {week_insights.get('week_summary', 'המשך מעקב שגרתי')}. {week_insights.get('recommendations', '')}"
    
    def _generate_appointment_response(self) -> str:
        """Generate appointment-related response"""
        return "אני יכול לעזור לך לתאם תורים ולנהל את הטיפול הטרום לידתי. איזה סוג תור תרצי לתאם?"
    
    def _generate_emergency_response(self, user_profile) -> str:
        """Generate emergency response"""
        if user_profile and user_profile.emergency_contact:
            return f"אם את חווה מצב חירום, אנא פני מיד לרופא המטפל. פרטי קשר חירום: {user_profile.emergency_contact}"
        else:
            return "אם את חווה מצב חירום, אנא פני מיד לרופא המטפל או לחדר המיון הקרוב."
    
    def _generate_general_response(self, message: str, actions: List) -> str:
        """Generate a general response"""
        if actions:
            action_descriptions = [action.description for action in actions[:2]]
            return f"אני מבין שאת שואלת על '{message}'. אני יכול לעזור לך עם: {', '.join(action_descriptions)}. במה תרצי להתמקד?"
        else:
            return "אני כאן לתמוך בך לאורך כל מסע ההריון. אני יכול לעזור לך בניהול מסמכים רפואיים, מעקב הריון, תזמון תורים ועוד. מה תרצי לדעת?"

# Global instance
chat_router = ChatRouter()
