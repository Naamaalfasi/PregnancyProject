"""
Medical Data Processing Agent
This file contains methods for extracting medical data and generating summaries using AI models.
"""

import httpx
from typing import Dict, Any
from app.config import settings

class MedicalDataProcessor:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_HOST
        
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

        async with httpx.AsyncClient(timeout=3600.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "pregnancy-assistant",
                    "prompt": prompt.format(text=text),
                    "stream": False
                }
            )

            if response.status_code == 200:
                result = response.json()
                summary = result["response"]

                return summary
            else:
                return "Error generating summary"

    async def generate_summary(self, text: str) -> str:
        """
        Generate a comprehensive summary of the medical document using Ollama
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

        async with httpx.AsyncClient(timeout=3600.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "pregnancy-assistant",
                    "prompt": prompt.format(text=text),
                    "stream": False
                }
            )

            if response.status_code == 200:
                result = response.json()
                summary = result["response"]

                return summary
            else:
                return "Error generating summary"
