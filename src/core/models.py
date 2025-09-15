"""
Data models using Pydantic for validation and type safety
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class TruckCondition(str, Enum):
    NEW = "New"
    USED = "Used"
    SECOND_HAND = "Second-Hand"

class TruckType(str, Enum):
    HORSEBOX = "horsebox"
    TACKBOX = "tackbox"
    GROOM_SUITE = "groom_suite"
    TRAILER = "trailer"

class Language(str, Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
    IT = "it"
    NL = "nl"

class Truck(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=200)
    price: int = Field(..., gt=0)
    year: int = Field(..., ge=2000, le=2030)
    condition: TruckCondition
    type: TruckType
    capacity: str
    features: List[str] = Field(default_factory=list)
    description: str = ""
    image_url: Optional[str] = None
    url: Optional[str] = None

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class FinancingOption(BaseModel):
    name: str
    apr: float = Field(..., ge=0, le=50)
    term_months: int = Field(..., gt=0, le=120)
    min_down_payment: float = Field(..., ge=0, le=1)
    description: str = ""

class ChatMessage(BaseModel):
    content: str = Field(..., min_length=1)
    is_user: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    language: Language = Language.EN

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserContext(BaseModel):
    budget: Optional[int] = None
    truck_preference: Optional[str] = None
    language: Language = Language.EN
    session_id: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)

class CompanyInfo(BaseModel):
    name: str
    phone: str
    email: str
    address: str
    hours: Dict[str, str]
    services: List[str]