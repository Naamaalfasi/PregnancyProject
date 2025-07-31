import PyPDF2
import io
from typing import List, Dict, Any
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.supported_types = ['blood_test', 'ultrasound', 'doctor_note', 'prescription', 'other']
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            logger.info(f"Successfully extracted text from PDF ({len(text)} characters)")
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            if end < len(text):
                # Find the last complete sentence or word boundary
                last_period = chunk.rfind('.')
                last_space = chunk.rfind(' ')
                split_point = max(last_period, last_space)
                
                if split_point > start + chunk_size // 2:
                    chunk = chunk[:split_point + 1]
                    end = start + split_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        logger.info(f"Created {len(chunks)} text chunks")
        return chunks
    
    def extract_metadata(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract relevant metadata from document text"""
        metadata = {
            "doc_type": doc_type,
            "extraction_date": datetime.utcnow().isoformat(),
            "text_length": len(text),
            "has_numbers": any(char.isdigit() for char in text),
            "has_dates": self._contains_dates(text),
            "language": self._detect_language(text)
        }
        
        # Extract specific metadata based on document type
        if doc_type == "blood_test":
            metadata.update(self._extract_blood_test_metadata(text))
        elif doc_type == "ultrasound":
            metadata.update(self._extract_ultrasound_metadata(text))
        
        return metadata
    
    def _contains_dates(self, text: str) -> bool:
        """Check if text contains date patterns"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'\d{1,2}\.\d{1,2}\.\d{2,4}'
        ]
        return any(re.search(pattern, text) for pattern in date_patterns)
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        hebrew_chars = len([c for c in text if '\u0590' <= c <= '\u05FF'])
        english_chars = len([c for c in text if c.isalpha() and c.isascii()])
        
        if hebrew_chars > english_chars:
            return "hebrew"
        else:
            return "english"
    
    def _extract_blood_test_metadata(self, text: str) -> Dict[str, Any]:
        """Extract blood test specific metadata"""
        metadata = {
            "test_type": "blood_test",
            "has_abnormal_values": False,
            "test_date": None
        }
        
        # Look for abnormal values (high/low indicators)
        abnormal_patterns = [
            r'high|HIGH|High',
            r'low|LOW|Low',
            r'גבוה|נמוך',
            r'↑|↓'
        ]
        
        if any(re.search(pattern, text) for pattern in abnormal_patterns):
            metadata["has_abnormal_values"] = True
        
        # Extract test date
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        date_match = re.search(date_pattern, text)
        if date_match:
            metadata["test_date"] = date_match.group(1)
        
        return metadata
    
    def _extract_ultrasound_metadata(self, text: str) -> Dict[str, Any]:
        """Extract ultrasound specific metadata"""
        metadata = {
            "test_type": "ultrasound",
            "pregnancy_week": None,
            "has_abnormalities": False
        }
        
        # Look for pregnancy week
        week_pattern = r'(\d{1,2})\s*(שבוע|week|weeks)'
        week_match = re.search(week_pattern, text, re.IGNORECASE)
        if week_match:
            metadata["pregnancy_week"] = int(week_match.group(1))
        
        # Look for abnormalities
        abnormal_patterns = [
            r'abnormal|ABNORMAL|Abnormal',
            r'pathology|PATHOLOGY|Pathology',
            r'חריג|חריגה|חריגות'
        ]
        
        if any(re.search(pattern, text) for pattern in abnormal_patterns):
            metadata["has_abnormalities"] = True
        
        return metadata

# Global PDF processor instance
pdf_processor = PDFProcessor()