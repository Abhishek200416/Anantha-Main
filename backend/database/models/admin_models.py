from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid

# ============= ADMIN MODELS =============

class AdminLogin(BaseModel):
    email: str
    password: str

class WhatsAppNumber(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone: str  # WhatsApp number with country code
    name: str  # Owner name or label
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WhatsAppNumberCreate(BaseModel):
    phone: str
    name: str

class PaymentSettings(BaseModel):
    status: str  # "enabled", "disabled", "removed"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RazorpaySettings(BaseModel):
    key_id: str
    key_secret: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminProfileUpdate(BaseModel):
    mobile: Optional[str] = None
    email: Optional[str] = None

class AdminProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "admin_profile"
    mobile: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None

class SendOTPRequest(BaseModel):
    email: str

class VerifyOTPAndChangePassword(BaseModel):
    email: str
    otp: str
    new_password: str

class OTPVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email: str
    otp: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime

class BugReportCreate(BaseModel):
    email: str
    mobile: str
    issue_description: str
    photo_url: Optional[str] = None

class BugReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    mobile: str
    issue_description: str
    photo_url: Optional[str] = None
    status: str = "New"  # New, In Progress, Resolved
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BugReportStatusUpdate(BaseModel):
    status: str
