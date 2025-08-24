import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from datetime import datetime

class FileStorageService:
    def __init__(self, base_upload_path: str = "Uploads"):
        self.base_upload_path = Path(base_upload_path)
        
    def ensure_user_directory(self, user_id: str) -> Path:
        """Create user's document directory if it doesn't exist"""
        user_dir = self.base_upload_path / user_id / "Documents"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
        
    async def save_uploaded_file(self, user_id: str, file: UploadFile) -> str:
        """Save uploaded file and return the file path"""
        user_dir = self.ensure_user_directory(user_id)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = user_dir / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return str(file_path)
    
    async def read_file(self, file_path: str) -> bytes:
        """Read file content"""
        with open(file_path, "rb") as file:
            return file.read()
    
    def read_file_as_bytes(self, file_path: str) -> bytes:
        """Read file content as bytes (for PDF processing)"""
        with open(file_path, "rb") as file:
            return file.read()
        
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False