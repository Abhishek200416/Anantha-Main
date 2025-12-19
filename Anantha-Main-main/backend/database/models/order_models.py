from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

# ============= ORDER MODELS =============

class OrderItem(BaseModel):
    product_id: str
    name: str
    image: str
    weight: str
    price: float
    quantity: int
    description: Optional[str] = None

class OrderCreate(BaseModel):
    user_id: Optional[str] = "guest"
    customer_name: str
    email: str  # Changed from EmailStr to str for more flexibility
    phone: str
    whatsapp_number: str  # Customer's WhatsApp number (mandatory)
    address: Optional[str] = ""
    doorNo: Optional[str] = ""
    building: Optional[str] = ""
    street: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    pincode: Optional[str] = ""
    location: Optional[str] = ""  # Made optional, will use city as fallback
    items: List[OrderItem]
    subtotal: float
    delivery_charge: float
    total: float
    payment_method: str = "online"
    payment_sub_method: Optional[str] = None
    is_custom_location: bool = False  # True if city is "Others"
    custom_city: Optional[str] = None  # Custom city name entered by user
    custom_state: Optional[str] = None  # State for custom city
    distance_from_guntur: Optional[float] = None  # Distance in km

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    tracking_code: str
    user_id: str
    customer_name: str
    email: str  # Changed from EmailStr to str
    phone: str
    whatsapp_number: Optional[str] = None  # Customer's WhatsApp number
    address: str
    doorNo: Optional[str] = None
    building: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    location: str
    items: List[OrderItem]
    subtotal: float
    delivery_charge: float
    total: float
    payment_method: str
    payment_sub_method: Optional[str] = None
    payment_status: str = "pending"  # pending, completed, failed
    is_custom_location: bool = False  # True if city is "Others"
    custom_city: Optional[str] = None  # Custom city name entered by user
    custom_state: Optional[str] = None  # State for custom city
    distance_from_guntur: Optional[float] = None  # Distance in km
    custom_city_request: bool = False  # True if user requested a custom city
    order_status: str = "pending"  # pending, confirmed, cancelled, delivered
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_delivery: Optional[str] = None
    admin_notes: Optional[str] = None
    delivery_days: Optional[int] = None
    cancelled: bool = False
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None
    cancellation_fee: float = 0.0
