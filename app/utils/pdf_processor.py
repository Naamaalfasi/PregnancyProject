import PyPDF2
import fitz
import io
from typing import List, Dict, Any, Optional
import re
import httpx
from app.config import settings

class PDFProcessor:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_HOST
        
    def extract_text_from_pdf(self, pdf_file: bytes) -> str:
        """Extract text content from PDF file (including scanned images)"""
        try:
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # First try to get text directly
                page_text = page.get_text("text")
                
                # If no text found, try OCR
                if not page_text.strip():
                    # Convert page to image and use OCR
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    # For now, we'll use the basic text extraction
                    # You can add actual OCR here if needed
                    page_text = f"[Page {page_num + 1} - Image content detected]"
                
                text += page_text + "\n"
            
            doc.close()
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

    def _parse_medical_summary(self, summary_text: str) -> Dict[str, Any]:
        """
        Parse the Ollama-generated medical summary into a structured dictionary
        """
        data = {
            "test_type": "",
            "test_date": "",
            "blood_type": None,
            "medications": [],
            "height": None,
            "weight": None,
        }
        
        try:
            # Split by lines and parse each field
            lines = summary_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('And the text is:'):
                    continue
                
                # Parse Test Type
                if line.startswith('- Test Type:'):
                    test_type = line.replace('- Test Type:', '').strip().strip('()')
                    if test_type and test_type != 'None':
                        data["test_type"] = test_type
                
                # Parse Test Date
                elif line.startswith('- Test Date:'):
                    test_date = line.replace('- Test Date:', '').strip().strip('()')
                    if test_date and test_date != 'None':
                        data["test_date"] = test_date
                
                # Parse Blood Type
                elif line.startswith('- Blood type:'):
                    blood_type = line.replace('- Blood type:', '').strip().strip('()')
                    if blood_type and blood_type != 'None':
                        # Validate blood type format
                        if self._is_valid_blood_type(blood_type):
                            data["blood_type"] = blood_type
                
                # Parse Medications
                elif line.startswith('- Medications taken or given:'):
                    meds = line.replace('- Medications taken or given:', '').strip().strip('()')
                    if meds and meds != 'None' and meds.lower() != 'none':
                        # Split by commas if multiple medications
                        if ',' in meds:
                            data["medications"] = [med.strip() for med in meds.split(',')]
                        else:
                            data["medications"] = [meds]
                
                # Parse Height
                elif line.startswith('- Height of mother:'):
                    height_str = line.replace('- Height of mother:', '').strip().strip('()')
                    if height_str and height_str != 'None':
                        # Extract numeric value
                        height_match = re.search(r'(\d+(?:\.\d+)?)', height_str)
                        if height_match:
                            data["height"] = float(height_match.group(1))
                
                # Parse Weight
                elif line.startswith('- Weight of mother:'):
                    weight_str = line.replace('- Weight of mother:', '').strip().strip('()')
                    if weight_str and weight_str != 'None':
                        # Extract numeric value
                        weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_str)
                        if weight_match:
                            data["weight"] = float(weight_match.group(1))
        
        except Exception as e:
            print(f"Error parsing medical summary: {e}")
            # Return default data structure if parsing fails
            pass
        
        return data
        
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


    def _is_valid_blood_type(self, blood_type: str) -> bool:
        """Validate blood type format"""
        valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        return blood_type in valid_types
        

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