import PyPDF2
import io
from typing import List, Dict, Any
import re

class PDFProcessor:
    def __init__(self):
        pass
        
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
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
        return chunks
        
    def extract_medical_data(self, text: str) -> Dict[str, Any]:
        """Extract structured medical data from text"""
        data = {
            "test_type": None,
            "test_date": None,
            "results": {},
            "normal_ranges": {},
            "abnormal_values": []
        }
        
        # TODO: Implement more sophisticated medical data extraction
        # This is a basic implementation - can be enhanced with NLP/ML
        
        # Look for common medical test patterns
        if "תוצאות בדיקת דם" in text or "blood test" in text.lower():
            data["test_type"] = "blood_test"
            
        if "אולטרסאונד" in text or "ultrasound" in text.lower():
            data["test_type"] = "ultrasound"
            
        # Extract dates (basic pattern)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        dates = re.findall(date_pattern, text)
        if dates:
            data["test_date"] = dates[0]
            
        return data
        
    def generate_summary(self, text: str) -> str:
        """Generate a summary of the medical document"""
        # TODO: Implement AI-powered summarization
        # For now, return first 200 characters
        return text[:200] + "..." if len(text) > 200 else text