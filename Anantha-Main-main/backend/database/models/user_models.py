from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid

# ============= USER AUTHENTICATION MODELS =============

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuth(BaseModel):
    id_token: str
    
class PhoneAuth(BaseModel):
    phone: str
    otp: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    phone: Optional[str] = None
    auth_provider: str = "email"  # email, google, phone
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SavedUserDetails(BaseModel):
    identifier: str  # phone or email
    customer_name: str
    email: EmailStr
    phone: str
    doorNo: Optional[str] = None
    building: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    location: str

class CustomerData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    door_no: Optional[str] = None
    building: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
