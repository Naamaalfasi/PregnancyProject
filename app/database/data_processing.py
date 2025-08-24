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
    def process_user_profile_data(
        name: str,
        lmp_date: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Process and calculate pregnancy-related data for new user profile
        """
        processed_data = {
            "name": name,
            **kwargs
        }
        
        if lmp_date and lmp_date != "0":
            try:
                processed_data["lmp_date"] = lmp_date
                processed_data["pregnancy_week"] = PregnancyDataProcessor.calculate_pregnancy_week(lmp_date)
                processed_data["due_date"] = PregnancyDataProcessor.calculate_due_date(lmp_date)
                if processed_data["pregnancy_week"]:
                    processed_data["trimester"] = PregnancyDataProcessor.calculate_trimester(processed_data["pregnancy_week"])
            except Exception as e:
                print(f"Warning: Error processing pregnancy data: {e}")
                processed_data["pregnancy_week"] = None
                processed_data["due_date"] = None
                processed_data["trimester"] = "unknown"
        
        return processed_data

