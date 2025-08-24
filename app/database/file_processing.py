from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class DocumentStatus(str, Enum):
    UPLOADED = "Uploaded"
    PROCESSING = "AI-Processing"
    COMPLETED = "Done"
    FAILED = "Failed"