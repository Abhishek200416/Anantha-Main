"""Database Models Package - All Pydantic models for the application"""

# User models
from .user_models import (
    UserRegister,
    UserLogin,
    GoogleAuth,
    PhoneAuth,
    User,
    SavedUserDetails,
    CustomerData
)

# Product models
from .product_models import (
    Product,
    DiscountUpdate
)

# Order models
from .order_models import (
    OrderItem,
    OrderCreate,
    Order
)

# Location models
from .location_models import (
    Location,
    State
)

# Admin models
from .admin_models import (
    AdminLogin,
    WhatsAppNumber,
    WhatsAppNumberCreate,
    PaymentSettings,
    RazorpaySettings,
    AdminProfileUpdate,
    AdminProfile,
    SendOTPRequest,
    VerifyOTPAndChangePassword,
    OTPVerification,
    BugReportCreate,
    BugReport,
    BugReportStatusUpdate
)

__all__ = [
    # User models
    "UserRegister",
    "UserLogin",
    "GoogleAuth",
    "PhoneAuth",
    "User",
    "SavedUserDetails",
    "CustomerData",
    # Product models
    "Product",
    "DiscountUpdate",
    # Order models
    "OrderItem",
    "OrderCreate",
    "Order",
    # Location models
    "Location",
    "State",
    # Admin models
    "AdminLogin",
    "WhatsAppNumber",
    "WhatsAppNumberCreate",
    "PaymentSettings",
    "RazorpaySettings",
    "AdminProfileUpdate",
    "AdminProfile",
    "SendOTPRequest",
    "VerifyOTPAndChangePassword",
    "OTPVerification",
    "BugReportCreate",
    "BugReport",
    "BugReportStatusUpdate"
]
