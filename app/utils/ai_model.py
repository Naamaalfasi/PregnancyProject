import requests
import json
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self, ollama_host: str = None):
        self.ollama_host = ollama_host or settings.OLLAMA_HOST
        self.model_name = "llama2"  # Default model for chat/completion
        
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a response using Ollama"""
        try:
            url = f"{self.ollama_host}/api/generate"
            
            # Prepare the full prompt with context
            full_prompt = self._prepare_prompt(prompt, context)
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "אני מצטערת, לא הצלחתי ליצור תגובה כרגע.")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "אני מצטערת, נתקלתי בשגיאה בעיבוד הבקשה שלך."
    
    async def analyze_conversation(self, user_id: str, message: str, response: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a conversation turn using AI"""
        try:
            prompt = f"""
            Analyze this conversation turn:
            User message: {message}
            Agent response: {response}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide analysis in JSON format with:
            - intent: user's intent
            - sentiment: user's sentiment
            - topics: main topics discussed
            - action_needed: any action required
            - follow_up: suggested follow-up
            """
            
            ai_response = await self.generate_response(prompt)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(ai_response)
            except:
                # Fallback analysis
                analysis = {
                    "intent": "general",
                    "sentiment": "neutral",
                    "topics": ["pregnancy"],
                    "action_needed": False,
                    "follow_up": "continue_conversation"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}")
            return {
                "intent": "general",
                "sentiment": "neutral",
                "topics": ["pregnancy"],
                "action_needed": False,
                "follow_up": "continue_conversation"
            }
    
    async def generate_medical_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate medical review using AI"""
        try:
            documents = context.get("documents", [])
            user_id = context.get("user_id", "unknown")
            
            prompt = f"""
            Review these medical documents for user {user_id}:
            Documents: {json.dumps(documents, ensure_ascii=False)}
            
            Provide medical review in JSON format with:
            - summary: overall summary
            - findings: key findings
            - recommendations: medical recommendations
            - urgency: urgency level (low/medium/high)
            - next_steps: suggested next steps
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                review = json.loads(ai_response)
            except:
                review = {
                    "summary": "Medical documents reviewed",
                    "findings": "No significant findings",
                    "recommendations": "Continue regular monitoring",
                    "urgency": "low",
                    "next_steps": "Follow up with healthcare provider"
                }
            
            return review
            
        except Exception as e:
            logger.error(f"Error generating medical review: {e}")
            return {
                "summary": "Unable to review medical documents",
                "findings": "Review failed",
                "recommendations": "Consult healthcare provider",
                "urgency": "medium",
                "next_steps": "Manual review required"
            }
    
    async def generate_pregnancy_week_insights(self, user_id: str, week: int, 
                                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate insights for a specific pregnancy week"""
        try:
            prompt = f"""
            Provide insights for pregnancy week {week}:
            User ID: {user_id}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide insights in JSON format with:
            - week_summary: what happens this week
            - symptoms: common symptoms
            - recommendations: health recommendations
            - tests: recommended tests
            - tips: helpful tips
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                insights = json.loads(ai_response)
            except:
                insights = {
                    "week_summary": f"Pregnancy week {week} insights",
                    "symptoms": "Common pregnancy symptoms",
                    "recommendations": "Follow healthcare provider advice",
                    "tests": "Regular prenatal care",
                    "tips": "Rest and maintain healthy lifestyle"
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating pregnancy insights: {e}")
            return {
                "week_summary": f"Week {week} of pregnancy",
                "symptoms": "Consult healthcare provider",
                "recommendations": "Regular prenatal care",
                "tests": "As recommended by provider",
                "tips": "Maintain healthy lifestyle"
            }
    
    async def generate_pregnancy_education(self, user_id: str, week: int, 
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate pregnancy education content"""
        try:
            prompt = f"""
            Generate pregnancy education content for week {week}:
            User ID: {user_id}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide education in JSON format with:
            - title: education title
            - content: educational content
            - key_points: main points to remember
            - resources: additional resources
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                education = json.loads(ai_response)
            except:
                education = {
                    "title": f"Pregnancy Week {week} Education",
                    "content": f"Educational content for week {week}",
                    "key_points": ["Regular prenatal care", "Healthy lifestyle", "Rest"],
                    "resources": ["Healthcare provider", "Pregnancy books", "Online resources"]
                }
            
            return education
            
        except Exception as e:
            logger.error(f"Error generating pregnancy education: {e}")
            return {
                "title": f"Week {week} Education",
                "content": "Consult your healthcare provider for personalized education",
                "key_points": ["Regular care", "Healthy lifestyle"],
                "resources": ["Healthcare provider"]
            }
    
    async def analyze_contractions(self, user_id: str, contraction_data: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze contraction data using AI"""
        try:
            prompt = f"""
            Analyze this contraction data:
            User ID: {user_id}
            Contraction Data: {json.dumps(contraction_data, ensure_ascii=False)}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide analysis in JSON format with:
            - pattern: contraction pattern
            - intensity: estimated intensity
            - frequency: contraction frequency
            - recommendation: medical recommendation
            - urgency: urgency level
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                analysis = json.loads(ai_response)
            except:
                analysis = {
                    "pattern": "Regular contractions",
                    "intensity": "Moderate",
                    "frequency": "Normal",
                    "recommendation": "Continue monitoring",
                    "urgency": "low"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing contractions: {e}")
            return {
                "pattern": "Unable to analyze",
                "intensity": "Unknown",
                "frequency": "Unknown",
                "recommendation": "Consult healthcare provider",
                "urgency": "medium"
            }
    
    async def generate_appointment_recommendations(self, user_id: str, appointment_type: str, 
                                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate appointment recommendations"""
        try:
            prompt = f"""
            Generate appointment recommendations:
            User ID: {user_id}
            Appointment Type: {appointment_type}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide recommendations in JSON format with:
            - timing: recommended timing
            - preparation: preparation needed
            - questions: questions to ask
            - follow_up: follow-up recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                recommendations = json.loads(ai_response)
            except:
                recommendations = {
                    "timing": "As soon as possible",
                    "preparation": "Bring medical documents",
                    "questions": ["Current symptoms", "Medications", "Concerns"],
                    "follow_up": "Schedule follow-up appointment"
                }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating appointment recommendations: {e}")
            return {
                "timing": "Consult healthcare provider",
                "preparation": "Bring medical documents",
                "questions": ["Current symptoms", "Concerns"],
                "follow_up": "As recommended by provider"
            }
    
    async def generate_document_upload_recommendations(self, user_id: str, document_types: List[str], 
                                                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate document upload recommendations"""
        try:
            prompt = f"""
            Generate document upload recommendations:
            User ID: {user_id}
            Document Types: {document_types}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide recommendations in JSON format with:
            - priority: upload priority
            - format: preferred format
            - metadata: required metadata
            - processing: processing notes
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                recommendations = json.loads(ai_response)
            except:
                recommendations = {
                    "priority": "high",
                    "format": "PDF",
                    "metadata": ["date", "type", "provider"],
                    "processing": "Standard processing"
                }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating document recommendations: {e}")
            return {
                "priority": "medium",
                "format": "PDF",
                "metadata": ["date", "type"],
                "processing": "Standard processing"
            }
    
    async def generate_reminder_settings(self, user_id: str, reminder_type: str, 
                                       context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate reminder settings"""
        try:
            prompt = f"""
            Generate reminder settings:
            User ID: {user_id}
            Reminder Type: {reminder_type}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide settings in JSON format with:
            - frequency: reminder frequency
            - timing: best timing
            - method: reminder method
            - content: reminder content
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                settings = json.loads(ai_response)
            except:
                settings = {
                    "frequency": "daily",
                    "timing": "morning",
                    "method": "app_notification",
                    "content": "Daily pregnancy reminder"
                }
            
            return settings
            
        except Exception as e:
            logger.error(f"Error generating reminder settings: {e}")
            return {
                "frequency": "daily",
                "timing": "morning",
                "method": "app_notification",
                "content": "Daily reminder"
            }
    
    async def generate_emergency_recommendations(self, user_id: str, emergency_contact: str, 
                                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate emergency recommendations"""
        try:
            prompt = f"""
            Generate emergency recommendations:
            User ID: {user_id}
            Emergency Contact: {emergency_contact}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide recommendations in JSON format with:
            - when_to_call: when to call emergency
            - symptoms: emergency symptoms
            - actions: immediate actions
            - contacts: emergency contacts
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                recommendations = json.loads(ai_response)
            except:
                recommendations = {
                    "when_to_call": "Severe symptoms",
                    "symptoms": ["Severe pain", "Bleeding", "High fever"],
                    "actions": ["Call healthcare provider", "Go to emergency room"],
                    "contacts": [emergency_contact]
                }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating emergency recommendations: {e}")
            return {
                "when_to_call": "Severe symptoms",
                "symptoms": ["Severe pain", "Bleeding"],
                "actions": ["Call healthcare provider"],
                "contacts": [emergency_contact]
            }
    
    async def analyze_symptoms(self, user_id: str, tracking_type: str, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze symptoms using AI"""
        try:
            prompt = f"""
            Analyze symptoms:
            User ID: {user_id}
            Tracking Type: {tracking_type}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide analysis in JSON format with:
            - pattern: symptom pattern
            - severity: symptom severity
            - triggers: possible triggers
            - recommendations: recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                analysis = json.loads(ai_response)
            except:
                analysis = {
                    "pattern": "Regular symptoms",
                    "severity": "Mild",
                    "triggers": ["Normal pregnancy changes"],
                    "recommendations": "Continue monitoring"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing symptoms: {e}")
            return {
                "pattern": "Unable to analyze",
                "severity": "Unknown",
                "triggers": ["Consult healthcare provider"],
                "recommendations": "Consult healthcare provider"
            }
    
    async def enhance_memory_content(self, user_id: str, memory_type: str, content: str, 
                                   metadata: Dict = None) -> str:
        """Enhance memory content using AI"""
        try:
            prompt = f"""
            Enhance this memory content:
            User ID: {user_id}
            Memory Type: {memory_type}
            Content: {content}
            Metadata: {json.dumps(metadata, ensure_ascii=False) if metadata else 'None'}
            
            Provide enhanced content that is more detailed and informative.
            """
            
            enhanced_content = await self.generate_response(prompt)
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Error enhancing memory content: {e}")
            return content
    
    async def generate_conversation_insights(self, user_id: str, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for a conversation"""
        try:
            prompt = f"""
            Generate insights for this conversation:
            User ID: {user_id}
            Conversation: {json.dumps(conversation, ensure_ascii=False)}
            
            Provide insights in JSON format with:
            - key_topics: main topics discussed
            - user_needs: user's needs
            - sentiment: overall sentiment
            - suggestions: suggestions for next interaction
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                insights = json.loads(ai_response)
            except:
                insights = {
                    "key_topics": ["pregnancy"],
                    "user_needs": ["information"],
                    "sentiment": "neutral",
                    "suggestions": ["continue conversation"]
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating conversation insights: {e}")
            return {
                "key_topics": ["pregnancy"],
                "user_needs": ["information"],
                "sentiment": "neutral",
                "suggestions": ["continue conversation"]
            }
    
    async def analyze_medical_memory(self, user_id: str, document_type: str, content: str) -> Dict[str, Any]:
        """Analyze medical memory"""
        try:
            prompt = f"""
            Analyze this medical memory:
            User ID: {user_id}
            Document Type: {document_type}
            Content: {content}
            
            Provide analysis in JSON format with:
            - significance: medical significance
            - implications: implications for pregnancy
            - recommendations: medical recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                analysis = json.loads(ai_response)
            except:
                analysis = {
                    "significance": "Standard medical information",
                    "implications": "Continue monitoring",
                    "recommendations": "Follow healthcare provider advice"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing medical memory: {e}")
            return {
                "significance": "Unable to analyze",
                "implications": "Consult healthcare provider",
                "recommendations": "Consult healthcare provider"
            }
    
    async def analyze_pregnancy_memory(self, user_id: str, week: int, content: str) -> Dict[str, Any]:
        """Analyze pregnancy memory"""
        try:
            prompt = f"""
            Analyze this pregnancy memory:
            User ID: {user_id}
            Week: {week}
            Content: {content}
            
            Provide analysis in JSON format with:
            - week_relevance: relevance to pregnancy week
            - development: development insights
            - recommendations: week-specific recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                analysis = json.loads(ai_response)
            except:
                analysis = {
                    "week_relevance": "Standard pregnancy information",
                    "development": "Normal development",
                    "recommendations": "Continue regular care"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing pregnancy memory: {e}")
            return {
                "week_relevance": "Unable to analyze",
                "development": "Consult healthcare provider",
                "recommendations": "Consult healthcare provider"
            }
    
    async def generate_medical_memory_insights(self, user_id: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for medical memory"""
        try:
            prompt = f"""
            Generate insights for this medical memory:
            User ID: {user_id}
            Memory: {json.dumps(memory, ensure_ascii=False)}
            
            Provide insights in JSON format with:
            - medical_importance: medical importance
            - pregnancy_impact: impact on pregnancy
            - follow_up: follow-up needed
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                insights = json.loads(ai_response)
            except:
                insights = {
                    "medical_importance": "Standard medical information",
                    "pregnancy_impact": "Continue monitoring",
                    "follow_up": "Regular care"
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating medical memory insights: {e}")
            return {
                "medical_importance": "Unable to analyze",
                "pregnancy_impact": "Consult healthcare provider",
                "follow_up": "Consult healthcare provider"
            }
    
    async def generate_pregnancy_memory_insights(self, user_id: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for pregnancy memory"""
        try:
            prompt = f"""
            Generate insights for this pregnancy memory:
            User ID: {user_id}
            Memory: {json.dumps(memory, ensure_ascii=False)}
            
            Provide insights in JSON format with:
            - week_insights: insights for the week
            - development_tracking: development tracking
            - recommendations: week-specific recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                insights = json.loads(ai_response)
            except:
                insights = {
                    "week_insights": "Standard pregnancy information",
                    "development_tracking": "Normal development",
                    "recommendations": "Continue regular care"
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating pregnancy memory insights: {e}")
            return {
                "week_insights": "Unable to analyze",
                "development_tracking": "Consult healthcare provider",
                "recommendations": "Consult healthcare provider"
            }
    
    async def generate_memory_summary(self, user_id: str, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate memory summary for user"""
        try:
            prompt = f"""
            Generate a comprehensive memory summary:
            User ID: {user_id}
            Memories: {json.dumps(memories, ensure_ascii=False)}
            
            Provide summary in JSON format with:
            - overall_summary: overall summary
            - key_events: key events
            - patterns: identified patterns
            - recommendations: overall recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                summary = json.loads(ai_response)
            except:
                summary = {
                    "overall_summary": "Comprehensive pregnancy journey",
                    "key_events": ["Regular checkups", "Document uploads"],
                    "patterns": ["Regular monitoring", "Good compliance"],
                    "recommendations": "Continue current care plan"
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating memory summary: {e}")
            return {
                "overall_summary": "Unable to generate summary",
                "key_events": ["Various pregnancy events"],
                "patterns": ["Regular monitoring"],
                "recommendations": "Consult healthcare provider"
            }
    
    async def generate_task_insights(self, user_id: str, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate insights for a task"""
        try:
            prompt = f"""
            Generate insights for this task:
            User ID: {user_id}
            Task: {json.dumps(task, ensure_ascii=False)}
            Context: {json.dumps(context, ensure_ascii=False) if context else 'None'}
            
            Provide insights in JSON format with:
            - importance: task importance level
            - urgency: urgency level
            - recommendations: task-specific recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                insights = json.loads(ai_response)
            except:
                insights = {
                    "importance": "medium",
                    "urgency": "normal",
                    "recommendations": "Complete as scheduled"
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating task insights: {e}")
            return {
                "importance": "medium",
                "urgency": "normal",
                "recommendations": "Complete as scheduled"
            }
    
    async def generate_timeline_insights(self, user_id: str, current_week: int, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights for pregnancy timeline"""
        try:
            prompt = f"""
            Generate timeline insights:
            User ID: {user_id}
            Current Week: {current_week}
            Timeline: {json.dumps(timeline, ensure_ascii=False)}
            
            Provide insights in JSON format with:
            - progress: pregnancy progress analysis
            - milestones: upcoming milestones
            - recommendations: timeline-based recommendations
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                insights = json.loads(ai_response)
            except:
                insights = {
                    "progress": "Normal pregnancy progress",
                    "milestones": ["Continue regular monitoring"],
                    "recommendations": "Follow healthcare provider schedule"
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating timeline insights: {e}")
            return {
                "progress": "Normal pregnancy progress",
                "milestones": ["Continue regular monitoring"],
                "recommendations": "Follow healthcare provider schedule"
            }
    
    async def generate_pregnancy_summary(self, user_id: str, current_week: int, completed_milestones: List[Dict[str, Any]], upcoming_milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive pregnancy summary"""
        try:
            prompt = f"""
            Generate pregnancy summary:
            User ID: {user_id}
            Current Week: {current_week}
            Completed Milestones: {json.dumps(completed_milestones, ensure_ascii=False)}
            Upcoming Milestones: {json.dumps(upcoming_milestones, ensure_ascii=False)}
            
            Provide summary in JSON format with:
            - overall_progress: overall pregnancy progress
            - achievements: completed achievements
            - next_steps: recommended next steps
            - health_status: overall health status
            """
            
            ai_response = await self.generate_response(prompt)
            
            try:
                summary = json.loads(ai_response)
            except:
                summary = {
                    "overall_progress": f"Week {current_week} of pregnancy",
                    "achievements": ["Regular prenatal care"],
                    "next_steps": ["Continue monitoring"],
                    "health_status": "Good"
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating pregnancy summary: {e}")
            return {
                "overall_progress": f"Week {current_week} of pregnancy",
                "achievements": ["Regular prenatal care"],
                "next_steps": ["Continue monitoring"],
                "health_status": "Good"
            }
    
    def _prepare_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Prepare the full prompt with context"""
        if not context:
            return prompt
        
        context_str = json.dumps(context, ensure_ascii=False)
        return f"""
        Context: {context_str}
        
        {prompt}
        """

# Global instance
ai_model = AIModel() 