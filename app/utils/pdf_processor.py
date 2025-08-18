import PyPDF2
import io
from typing import List, Dict, Any
import re
import httpx
from app.config import settings

class PDFProcessor:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_HOST
        
    def extract_text_from_pdf(self, pdf_file: bytes) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
            
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        assert overlap < chunk_size, "Overlap must be smaller than chunk size"
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunks.append(text[start:end])
            if end == text_len:
                break
            start = start + chunk_size - overlap

        return chunks
        
    def extract_medical_data(self, text: str) -> Dict[str, Any]:
        """Extract structured medical data from text"""
        data = {
            "test_type": "",
            "test_date": "",
            "results": {},
            "normal_ranges": {},
            "abnormal_values": [],
            "recommendations": [],  # Added field for recommendations
            "key_findings": []      # Added field for key findings
        }
        
        # Look for common medical test patterns
        if "תוצאות בדיקת דם" in text or "blood test" in text.lower():
            data["test_type"] = "blood_test"
        elif "אולטרסאונד" in text or "ultrasound" in text.lower():
            data["test_type"] = "ultrasound"
        elif "בדיקת שתן" in text or "urine test" in text.lower():
            data["test_type"] = "urine_test"
        elif "בדיקה גנטית" in text or "genetic test" in text.lower():
            data["test_type"] = "genetic_test"
            
        # Extract dates (basic pattern)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        dates = re.findall(date_pattern, text)
        if dates:
            data["test_date"] = dates[0]
            
        return data
        

    async def generate_summary(self, text: str) -> str:
        """
        Generate a comprehensive summary of the medical document using Ollama
        Returns a dictionary with different aspects of the summary
        """
        prompt = """
        Given the following blood test results, summarize any key findings, including abnormal values, possible concerns, and recommendations.
        
        {text}
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