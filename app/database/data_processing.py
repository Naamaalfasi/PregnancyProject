import chromadb
import uuid
import json
import motor.motor_asyncio

from bson import json_util
from fastapi import HTTPException
from chromadb.config import Settings
from typing import List, Dict, Any
from pydoc import doc
from typing import List, Optional
from datetime import datetime, timedelta
from app.config import settings
from app.models.user import UserProfile
from app.utils.embeddings import EmbeddingGenerator


class PregnancyDataProcessor:
    """Handles pregnancy-related data calculations and processing"""
    
    @staticmethod
    def parse_ddmmyyyy(date_str: str) -> datetime:
        """
        Parse date string in DDMMYYYY format to datetime object
        """
        if not date_str or date_str == "0" or len(date_str) != 8:
            raise ValueError(f"Invalid date format: {date_str}. Expected DDMMYYYY format.")
        
        try:
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = int(date_str[4:8])
            
            # Validate date components
            if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
                raise ValueError(f"Invalid date values: day={day}, month={month}, year={year}")
            
            return datetime(year, month, day)
        except ValueError as e:
            raise ValueError(f"Failed to parse date '{date_str}': {str(e)}")
    
    @staticmethod
    def calculate_pregnancy_week(lmp_date: str) -> int:
        """
        Calculate pregnancy week based on Last Menstrual Period (LMP) in DDMMYYYY format
        Pregnancy is typically 40 weeks from LMP
        """
        try:
            today = datetime.now()
            lmp_datetime = PregnancyDataProcessor.parse_ddmmyyyy(lmp_date)
            weeks_pregnant = (today - lmp_datetime).days // 7
            return max(1, min(weeks_pregnant, 42))  # Clamp between 1-42 weeks
        except ValueError as e:
            print(f"Warning: Could not calculate pregnancy week: {e}")
            return None
    
    @staticmethod
    def calculate_due_date(lmp_date: str) -> str:
        """
        Calculate estimated due date (40 weeks from LMP) from DDMMYYYY format
        Returns ISO format string to match the model
        """
        try:
            lmp_datetime = PregnancyDataProcessor.parse_ddmmyyyy(lmp_date)
            due_datetime = lmp_datetime + timedelta(weeks=40)
            return due_datetime.isoformat()
        except ValueError as e:
            print(f"Warning: Could not calculate due date: {e}")
            return None
    
    @staticmethod
    def calculate_trimester(pregnancy_week: int) -> str:
        """
        Determine which trimester the pregnancy is in
        """
        if pregnancy_week is None:
            return "unknown"
        elif pregnancy_week <= 13:
            return "first"
        elif pregnancy_week <= 26:
            return "third"
        else:
            return "third"

    @staticmethod
    def calculate_age(date_of_birth: str) -> Optional[int]:
        """
        Calculate age from date of birth in DDMMYYYY format
        Returns age in years
        """
        if not date_of_birth or date_of_birth == "None-String" or date_of_birth == "0":
            return None
            
        try:
            birth_datetime = PregnancyDataProcessor.parse_ddmmyyyy(date_of_birth)
            today = datetime.now()
            
            # Calculate age
            age = today.year - birth_datetime.year
            
            # Adjust if birthday hasn't occurred this year
            if today.month < birth_datetime.month or (today.month == birth_datetime.month and today.day < birth_datetime.day):
                age -= 1
                
            return max(0, age)  # Ensure age is not negative
        except ValueError as e:
            print(f"Warning: Could not calculate age from date of birth '{date_of_birth}': {e}")
            return None

    

