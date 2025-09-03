"""
Medical Data Processing Agent
This file contains methods for extracting medical data and generating summaries using AI models.
"""

import google.generativeai as genai
from typing import Any, Dict
from app.config import settings


class MedicalDataProcessor:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self._gemini = genai.GenerativeModel(settings.GEMINI_MODEL)
        
    async def extract_medical_data(self, text: str) -> str:
        """
        Extract specific medical data from the text
        """
        prompt = """
        Given the following text, you need to extract specific medical data from it,
        Response must be according the format below, No free text, and only legal values that are mentioned. 
        if data not found, return None for that field:
        - Test Type: [blood_test, ultrasound, urine_test, genetic_test, other]
        - Test Date: [DDMMYYYY or None]
        - Blood type: [A+, A-, B+, B-, AB+, AB-, O+, O-, None]
        - Medications taken or given: [None or list of medications]
        - Allergies: [None or list of allergies]
        - Height of mother: [in cm or None]
        - Weight of mother: [in kg or None]

        And the text is: {text}
        """
        try:
            resp = self._gemini.generate_content(prompt.format(text=text))
            return resp.text if hasattr(resp, "text") else str(resp)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                return "Quota exceeded. Please try again later."
            raise

    async def generate_summary(self, text: str) -> str:
        """
        Generate a comprehensive summary of the medical document using Gemini
        Returns a dictionary with different aspects of the summary
        """
        prompt = """
        Given the following blood test results, summarize it in a structured format.
        desired output:
        - Test Type (blood_test, ultrasound, etc..)
        - Test Date
        - Abnormal Values (if any)
        - Possible Concerns (if any)
        - Recommendations (if any)
        - is mother in risk of immidiate danger? (yes/no only)
        - is fetus in risk of immidiate danger? (yes/no only) 

        And the text is: {text}
        """
        try:
            resp = self._gemini.generate_content(prompt.format(text=text))
            return resp.text if hasattr(resp, "text") else str(resp)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                return "Quota exceeded. Please try again later."
            raise