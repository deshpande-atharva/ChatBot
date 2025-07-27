from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    active = "active"
    completed = "completed"

class MessageSender(str, Enum):
    user = "user"
    bot = "bot"

class VehicleUse(str, Enum):
    commuting = "commuting"
    commercial = "commercial"
    farming = "farming"
    business = "business"

class LicenseType(str, Enum):
    foreign = "foreign"
    personal = "personal"
    commercial = "commercial"

class LicenseStatus(str, Enum):
    valid = "valid"
    suspended = "suspended"

# Request models
class SessionCreate(BaseModel):
    pass

class MessageCreate(BaseModel):
    session_id: str
    sender: MessageSender
    content: str

class VehicleCreate(BaseModel):
    session_id: str
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    body_type: Optional[str] = None
    vehicle_use: VehicleUse
    blind_spot_warning: bool
    commute_days_per_week: Optional[int] = None
    commute_one_way_miles: Optional[float] = None
    annual_mileage: Optional[int] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

# Response models
class SessionResponse(BaseModel):
    id: str
    status: SessionStatus
    current_step: str
    created_at: datetime
    data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: str
    session_id: str
    sender: MessageSender
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class VehicleResponse(BaseModel):
    id: str
    session_id: str
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    body_type: Optional[str] = None
    vehicle_use: VehicleUse
    blind_spot_warning: bool
    commute_days_per_week: Optional[int] = None
    commute_one_way_miles: Optional[float] = None
    annual_mileage: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    message: str
    current_step: str
    session_status: SessionStatus