from typing import Optional, List
from datetime import datetime
import uuid
from app.database.mongo_client import MongoDBClient
from app.models.chat import Conversation, ChatMessage
from app.models.user import UserProfile
import google.generativeai as genai
from fastapi import HTTPException


class ChatService:
    def __init__(self, mongo_client: MongoDBClient, gemini: genai.GenerativeModel):
        self.mongo_client = mongo_client
        self.token_limit = 4000
        self.warning_threshold = 3200  # 80% of limit
        self._gemini = gemini
    
    async def should_archive_conversation(self, conversation: Conversation, new_message: str) -> bool:
        """Check if conversation should be archived after adding new message"""
        current_tokens =  len(str((await self.get_conversation_context(conversation)))) // 4
        new_message_tokens = len(new_message) // 4
        
        # If current + new message exceeds 80% of limit (3200), archive after this exchange
        return (current_tokens + new_message_tokens) >= self.warning_threshold
    
    async def generate_subject(self, first_message: str) -> str:
        """Generate conversation subject from first message"""
        # First 30 characters or 6 words, whichever is shorter
        if len(first_message) <= 30:
            return first_message
        
        words = first_message.split()
        if len(words) <= 6:
            return first_message
        
        return " ".join(words[:6])
    
    async def create_new_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation and set as active"""
        conversation_id = str(uuid.uuid4())

        system_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            role="system",
            content="""You are part of a comprehensive pregnancy application that provides:

                        SERVICES:
                        - Pregnancy week tracking and milestone guidance
                        - Medical document analysis and storage
                        - Personalized task recommendations
                        - Nutritional and lifestyle advice
                        - Symptom monitoring and guidance
                        - Appointment scheduling reminders
                        - Profile updates

                        YOUR ROLE:
                        - You are a pregnancy knowledge assistant that provides detailed, evidence-based educational information, tailored recommendations, and support based on user input.
                        - Provide evidence-based answers for pregnancy-related questions
                        - Offer personalized recommendations based on the user's profile and the conversation history
                        - Support users with pregnancy concerns and questions
                        - refering the user to other sources of information is only allowed if explicitly asked.

                        Any text from here will be either metadata, context, or user's messages. Good luck! """,

            timestamp=datetime.utcnow()
        )
        
        conversation = Conversation(
            conversation_id=conversation_id,
            subject="New Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            messages=[system_message]
        )
        
        await self.mongo_client.create_conversation(user_id, conversation)
        
        return conversation
    
    async def add_message_to_conversation(self, user_id: str, conversation_id: str, role: str, content: str):
        """Add a message to a conversation"""
        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )

        conversation = await self.mongo_client.get_conversation(user_id, conversation_id)
        if conversation.subject == "New Conversation":
            subject = await self.generate_subject(content)
            await self.mongo_client.db.user_profiles.update_one(
                {"user_id": user_id, "conversations.conversation_id": conversation_id},
                {"$set": {"conversations.$.subject": subject}}
            )

        await self.mongo_client.add_message_to_conversation(user_id, conversation_id, message)
        return True
    
    async def get_conversation_context(self, conversation: Conversation) -> str:
        """Get conversation context"""
        context = ""
        for message in conversation.messages:
            context += f"{message.role}: {message.content}\n"
        return context

    async def analyze_profile_updates(self, user: UserProfile, user_message: str, context: str) -> str:
        """AI 1: Analyze message for potential profile updates"""
        filtered_user = user.dict(exclude={'conversations'})
        
        profile_analysis_prompt = f"""
        You are a profile update analyzer for a pregnancy application.

        Analyze the user's message to detect if they are providing information that should update their profile.
        
        Look for:
        - Personal information (weight, height, age, blood type, name)
        - Pregnancy-related dates (LMP date, due date)
        - Medical information (allergies, medications, conditions)
        - Any factual statements about themselves
        
        If you detect profile updates needed, respond with:
        !$UPDATE$numOfUpdates$field_name1$value1$field_name2$value2$!
        
        Available fields: weight, height, age, blood_type, name, lmp_date, due_date, allergies, medications, medical_conditions
        
        Examples:
        - "My blood type is AB-" → !$UPDATE$1$blood_type$AB-$!
        - "I weigh 65kg and I'm 30 years old" → !$UPDATE$2$weight$65kg$age$30$!
        - "I have no allergies" → !$UPDATE$1$allergies$[]$!
        
        If NO profile updates are needed, respond with: NO_UPDATE. 

        Here are the user's profile and the conversation history:
        
        USER PROFILE: {filtered_user}
        CONVERSATION HISTORY: {context}
        USER MESSAGE: {user_message}        
        
        Your analysis:
        """
        
        try:
            response = self._gemini.generate_content(profile_analysis_prompt)
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            print(f"Profile analysis error: {e}")
            return "NO_UPDATE"

    async def generate_organic_response(self, user: UserProfile, user_message: str, context: str, profile_updates_applied: List[dict]) -> str:
        """AI 2: Generate organic response based on user profile"""
        filtered_user = user.dict(exclude={'conversations'})

        # Detect if the user message is in Hebrew (basic heuristic: presence of Hebrew unicode range)
        is_hebrew = any('\u0590' <= ch <= '\u05FF' for ch in user_message)
        language_instruction = (
            "IMPORTANT: Respond in Hebrew (עברית תקנית), keep the entire answer in Hebrew."
            if is_hebrew else
            "IMPORTANT: Respond in the user's language."
        )

        organic_prompt = f"""

        ANSWER THE USER'S QUESTION BASED ON THE USER'S PROFILE AND THE CONVERSATION HISTORY.
        Avoid hallucinations; if unsure, say what info is needed.
        
        USER PROFILE: {filtered_user}
        CONVERSATION HISTORY: {context}
        USER MESSAGE: {user_message}
        PROFILE UPDATES APPLIED: {profile_updates_applied}
        Provide a helpful, personalized response based on the user's profile and their question.

        Major guidelines:
        - If they ask about medical documents, direct them to upload through the app.
        - If profile updates were applied - Update the user, If not - do not mention it.
        - If question is not related to pregnancy, do not answer it.
        Your response:
        """

        response = self._gemini.generate_content(organic_prompt)
        return response.text if hasattr(response, "text") else str(response)

    
    async def process_chat_message(self, user_id: str, message: str) -> dict:
        """Main method to process a chat message"""
        # Get user profile
        user = await self.mongo_client.get_user_profile(user_id)
        if not user:
            return False
        
        # Get or create active conversation
        active_conversation = await self.mongo_client.get_active_conversation(user_id)
        if not active_conversation:
            active_conversation = await self.create_new_conversation(user_id)


        context = await self.get_conversation_context(active_conversation)
        
        # Check if we should archive after this exchange
        should_archive = await self.should_archive_conversation(active_conversation, message)
        
        # Add user message
        await self.add_message_to_conversation(
            user_id, 
            active_conversation.conversation_id, 
            "user", 
            message
        )
        
        # Generate AI response
        organic_response = ""
        profile_updates_applied = []
        try:
            profile_update_analysis = await self.analyze_profile_updates(user, message, context)

            if profile_update_analysis and profile_update_analysis != "NO_UPDATE":
                profile_updates_applied = await self.parse_and_execute_profile_updates(user_id, profile_update_analysis)

            organic_response = await self.generate_organic_response(user, message, context, profile_updates_applied)

        except Exception as e:
            organic_response = "I'm sorry, I couldn't process your message. Please try again."
            err_msg = str(e)
            if "429" in err_msg or "ResourceExhausted" in err_msg:
                raise HTTPException(status_code=429, detail="Gemini quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail="Gemini error: " + err_msg)


        # Add AI response
        await self.add_message_to_conversation(
            user_id, 
            active_conversation.conversation_id, 
            "ai", 
            organic_response
        )
        
        # Archive conversation if needed
        if should_archive:
            await self.create_new_conversation(user_id)
            return {
                "response": organic_response, 
                "Profile_updates_applied": profile_updates_applied,
                "conversation_archived": True,
                "conversation_id": active_conversation.conversation_id
            }
        
        return {
            "response": organic_response, 
            "Profile_updates_applied": profile_updates_applied,
            "conversation_archived": False,
            "conversation_id": active_conversation.conversation_id
        }

    async def switch_to_conversation(self, user_id: str, conversation_id: str) -> Conversation:
        """Switch to a specific conversation"""
        conversation = await self.mongo_client.get_conversation(user_id, conversation_id)
        await self.mongo_client.set_active_conversation(user_id, conversation_id)
        return conversation

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        conversations = await self.mongo_client.get_user_conversations(user_id)
        if not conversations:
            return []
        return conversations
    
    async def get_conversation_by_id(self, user_id: str, conversation_id: str) -> Optional[Conversation]:
        """Get specific conversation by ID"""
        conversation = await self.mongo_client.get_conversation(user_id, conversation_id)
        if not conversation:
            return None
        return conversation

    async def parse_and_execute_profile_updates(self, user_id: str, update_command: str) -> List[dict]:
        """Parse profile update command and execute updates, return list of applied updates"""
        import re
        
        # Pattern to match !$UPDATE$numOfUpdates$field_name1$value1$field_name2$value2$!
        pattern = r'!\$UPDATE\$(\d+)\$([^!]+)\$!'
        match = re.match(pattern, update_command)
        
        applied_updates = []
        
        if match:
            num_updates = int(match.group(1))
            fields_data = match.group(2)
            
            # Parse field-value pairs
            field_value_pairs = fields_data.split('$')
            
            # Validate number of pairs matches expected count
            if len(field_value_pairs) == num_updates * 2:
                # Execute all updates
                for i in range(0, len(field_value_pairs), 2):
                    field = field_value_pairs[i]
                    value = field_value_pairs[i + 1]
                    
                    success = await self.execute_profile_update(user_id, field, value)
                    applied_updates.append({
                        "field": field,
                        "value": value,
                        "success": success
                    })
        
        return applied_updates

    async def execute_profile_update(self, user_id: str, field: str, value: str) -> bool:
        """Execute single profile update and return success status"""
        field_mapping = {
            'weight': 'weight',
            'height': 'height',
            'pregnancy_week': 'pregnancy_week',
            'blood_type': 'blood_type',
            'age': 'age',
            'lmp_date': 'lmp_date',
            'due_date': 'due_date',
            'name': 'name',
            'allergies': 'allergies',
            'medications': 'medications',
            'medical_conditions': 'medical_conditions'
        }
        
        if field in field_mapping:
            db_field = field_mapping[field]
            converted_value = self._convert_field_value(db_field, value)
            
            if converted_value is not None:
                try:
                    await self.mongo_client.update_one(user_id, db_field, converted_value)
                    return True
                except Exception as e:
                    print(f"Error updating {field}: {e}")
                    return False
        return False

    def _convert_field_value(self, field: str, value: str):
        """Convert string value to appropriate type for database field"""
        try:
            if field in ['weight', 'height']:
                # Extract number from string like "60kg" or "165cm"
                import re
                number = re.findall(r'[\d.]+', value)
                if number:
                    return float(number[0])
            elif field == 'pregnancy_week':
                return int(value)
            elif field == 'age':
                return int(value)
            elif field in ['allergies', 'medications', 'medical_conditions']:
                # Handle list fields
                if value == "[]":
                    return []
                # If it's a string representation of a list, parse it
                if value.startswith('[') and value.endswith(']'):
                    try:
                        import ast
                        return ast.literal_eval(value)
                    except:
                        return [value]
                return [value]
            elif field in ['blood_type', 'name', 'due_date', 'lmp_date']:
                return value
            else:
                return value
        except (ValueError, TypeError):
            return None   

    async def delete_conversation(self, user_id: str, conversation_id: str) -> dict:
        """Delete a conversation"""
        try:
            # Delete the conversation from MongoDB
            result = await self.mongo_client.delete_conversation(user_id, conversation_id)
            return {"success": True, "deleted": result}
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return {"success": False, "error": str(e)}

    async def get_active_conversation_details(self, user_id: str) -> Optional[Conversation]:
        """Get the active conversation with full details"""
        active_conversation = await self.mongo_client.get_active_conversation(user_id)
        return active_conversation
