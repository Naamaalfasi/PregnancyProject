import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from app.models.user import UserProfile
from app.config import settings

template = """
Answer the question below.

USER PROFILE: {UserProfile}

HERE is the conversation history: {context}

Question: {question}

IMPORTANT: 
- Use the UserProfile ONLY to personalize the answer.
- Consider the user's pregnancy week, medical conditions, and allergies
- Provide safe, evidence-based pregnancy advice
- If medical concerns arise, suggest consulting a healthcare provider
- Be supportive and informative
- If the private context is missing or not relevant, answer from your general medical knowledge.
- Prioritize safety; avoid diagnoses; suggest consulting a healthcare provider when appropriate.

Answer:
"""

genai.configure(api_key=settings.GOOGLE_API_KEY)
_gemini = genai.GenerativeModel(settings.GEMINI_MODEL)
prompt = ChatPromptTemplate.from_template(template)

def _invoke(payload: dict) -> str:
    rendered = prompt.format(**payload)
    resp = _gemini.generate_content(rendered)
    return resp.text if hasattr(resp, "text") else str(resp)

class ChainAdapter:
    def invoke(self, payload: dict) -> str:
        return _invoke(payload)

chain = ChainAdapter()