from fastapi import FastAPI, APIRouter, HTTPException, Depends, File, UploadFile, Header, Request, Form
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict, ValidationError
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import aiofiles
import base64
from auth import create_access_token, decode_token, get_password_hash, verify_password
from email_service import send_order_confirmation_email
from gmail_service import send_order_confirmation_email_gmail, send_order_status_update_email, send_city_approval_email, send_city_rejection_email
from cities_data import ALL_CITIES, DEFAULT_DELIVERY_CHARGES, DEFAULT_OTHER_CITY_CHARGE, ANDHRA_PRADESH_CITIES, TELANGANA_CITIES
import random
import string
from math import radians, sin, cos, sqrt, atan2
import razorpay
import hmac
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID', ''), os.environ.get('RAZORPAY_KEY_SECRET', '')))

# Create the main app
app = FastAPI()

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add validation error handler to log details
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"VALIDATION ERROR on {request.url.path}")
    print(f"Request body: {await request.body()}")
    print(f"Validation errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# ============= MODELS =============

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

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    name_telugu: Optional[str] = None  # Telugu name for the product
    category: str
    description: str
    description_telugu: Optional[str] = None  # Telugu description for the product
    image: str
    prices: List[dict]
    isBestSeller: bool = False
    isNew: bool = False
    tag: str = "Traditional"
    discount_percentage: Optional[float] = None
    discount_expiry_date: Optional[str] = None
    inventory_count: Optional[int] = None
    out_of_stock: bool = False
    available_cities: Optional[List[str]] = None  # Cities where product can be delivered

class DiscountUpdate(BaseModel):
    discount_percentage: float
    discount_expiry_date: str

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

class Location(BaseModel):
    name: str
    charge: float
    free_delivery_threshold: Optional[float] = None  # City-specific free delivery threshold
    state: Optional[str] = None

class State(BaseModel):
    name: str
    enabled: bool = True

class AdminLogin(BaseModel):
    email: str
    password: str

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

# ============= WHATSAPP & PAYMENT SETTINGS MODELS =============

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

# ============= HELPER FUNCTIONS =============

def generate_order_id():
    """Generate unique order ID"""
    return f"AL{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_tracking_code():
    """Generate tracking code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if it's an admin user
        if payload.get("is_admin") or payload.get("sub") == "admin":
            return {
                "id": "admin",
                "email": "admin@ananthalakshmi.com",
                "name": "Admin",
                "is_admin": True
            }
        
        user = await db.users.find_one({"id": payload.get("sub")}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from JWT token - allows guest users"""
    if not authorization:
        # Return guest user
        return {
            "id": "guest",
            "email": "guest@ananthalakshmi.com",
            "name": "Guest",
            "is_admin": False
        }
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            # Return guest user if token is invalid
            return {
                "id": "guest",
                "email": "guest@ananthalakshmi.com",
                "name": "Guest",
                "is_admin": False
            }
        
        # Check if it's an admin user
        if payload.get("is_admin") or payload.get("sub") == "admin":
            return {
                "id": "admin",
                "email": "admin@ananthalakshmi.com",
                "name": "Admin",
                "is_admin": True
            }
        
        user = await db.users.find_one({"id": payload.get("sub")}, {"_id": 0, "password": 0})
        if not user:
            # Return guest user if user not found
            return {
                "id": "guest",
                "email": "guest@ananthalakshmi.com",
                "name": "Guest",
                "is_admin": False
            }
        
        return user
    except Exception as e:
        # Return guest user for any authentication error
        return {
            "id": "guest",
            "email": "guest@ananthalakshmi.com",
            "name": "Guest",
            "is_admin": False
        }

# ============= AUTHENTICATION APIS =============

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register new user with email and password"""
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "name": user_data.name,
        "phone": user_data.phone,
        "password": hashed_password,
        "auth_provider": "email",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user)
    
    # Create token
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    
    # Remove password and _id from response
    user.pop("password", None)
    user.pop("_id", None)
    
    return {
        "user": user,
        "token": token,
        "message": "Registration successful"
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    """Login with email and password"""
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    
    if not user or not verify_password(user_data.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    
    # Remove password from response
    user.pop("password", None)
    
    return {
        "user": user,
        "token": token,
        "message": "Login successful"
    }

@api_router.post("/auth/google")
async def google_auth(auth_data: GoogleAuth):
    """Google OAuth authentication (mock implementation)"""
    # In production, verify the id_token with Google
    # For now, this is a mock implementation
    
    # Mock user data
    user_email = f"user{random.randint(1000, 9999)}@gmail.com"
    user_name = "Google User"
    
    # Check if user exists
    user = await db.users.find_one({"email": user_email}, {"_id": 0})
    
    if not user:
        # Create new user
        user = {
            "id": str(uuid.uuid4()),
            "email": user_email,
            "name": user_name,
            "auth_provider": "google",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user)
        user.pop("_id", None)
    
    # Create token
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    
    return {
        "user": user,
        "token": token,
        "message": "Google authentication successful"
    }

@api_router.post("/auth/phone")
async def phone_auth(auth_data: PhoneAuth):
    """Phone OTP authentication (mock implementation)"""
    # In production, verify OTP
    # For now, this is a mock implementation
    
    # Mock OTP verification (assume OTP is correct)
    user = await db.users.find_one({"phone": auth_data.phone}, {"_id": 0})
    
    if not user:
        # Create new user
        user = {
            "id": str(uuid.uuid4()),
            "email": f"{auth_data.phone}@phone.user",
            "name": f"User {auth_data.phone}",
            "phone": auth_data.phone,
            "auth_provider": "phone",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user)
        user.pop("_id", None)
    
    # Create token
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    
    return {
        "user": user,
        "token": token,
        "message": "Phone authentication successful"
    }

@api_router.post("/auth/admin-login")
async def admin_login(login_data: AdminLogin):
    """Admin login with email and password - returns JWT token"""
    
    # First, check if admin profile exists in database with custom credentials
    admin_profile = await db.admin_profile.find_one({"id": "admin_profile"}, {"_id": 0})
    
    password_valid = False
    email_valid = False
    admin_email = "admin@ananthalakshmi.com"  # Default email
    
    # If admin profile exists with custom credentials, verify against that
    if admin_profile and admin_profile.get("password_hash") and admin_profile.get("email"):
        # Verify email matches
        email_valid = login_data.email.lower() == admin_profile["email"].lower()
        # Verify password
        password_valid = verify_password(login_data.password, admin_profile["password_hash"])
        admin_email = admin_profile["email"]
    else:
        # Fall back to default credentials
        DEFAULT_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@ananthalakshmi.com')
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
        email_valid = login_data.email.lower() == DEFAULT_EMAIL.lower()
        password_valid = login_data.password == ADMIN_PASSWORD
        admin_email = DEFAULT_EMAIL
    
    if not email_valid:
        raise HTTPException(status_code=401, detail="Invalid admin email")
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    
    # Create admin user object
    admin_user = {
        "id": "admin",
        "email": admin_email,
        "name": "Admin",
        "is_admin": True
    }
    
    # Create token with long expiration for admin
    token = create_access_token({"sub": admin_user["id"], "email": admin_user["email"], "is_admin": True})
    
    return {
        "user": admin_user,
        "token": token,
        "message": "Admin login successful"
    }

@api_router.get("/user-details/{identifier}")
async def get_saved_user_details(identifier: str):
    """Get saved user details by phone or email"""
    details = await db.saved_user_details.find_one({"identifier": identifier}, {"_id": 0})
    
    if not details:
        return None
    
    return details

# ============= PRODUCTS APIS =============

@api_router.get("/products")
async def get_products(city: Optional[str] = None, state: Optional[str] = None):
    """Get all products with discount calculation, optionally filtered by city/state availability"""
    # Build query filter
    query_filter = {}
    if city:
        # Filter products that either have no city restriction or include the requested city
        query_filter = {
            "$or": [
                {"available_cities": None},
                {"available_cities": []},
                {"available_cities": city}
            ]
        }
    elif state:
        # Filter products by state - get all cities in that state and filter
        state_cities = await db.locations.find({"state": state}, {"name": 1, "_id": 0}).to_list(1000)
        city_names = [city_doc["name"] for city_doc in state_cities]
        query_filter = {
            "$or": [
                {"available_cities": None},
                {"available_cities": []},
                {"available_cities": {"$in": city_names}}
            ]
        }
    
    products = await db.products.find(query_filter, {"_id": 0}).to_list(1000)
    
    # Calculate discounted prices for each product
    for product in products:
        discount_percentage = product.get('discount_percentage')
        discount_expiry = product.get('discount_expiry_date')
        
        # Check if discount is valid
        discount_active = False
        if discount_percentage and discount_expiry:
            try:
                # Parse the date string
                expiry_date_str = discount_expiry.replace('Z', '+00:00')
                if 'T' in expiry_date_str:
                    expiry_date = datetime.fromisoformat(expiry_date_str)
                else:
                    # If only date is provided (YYYY-MM-DD), add time and timezone
                    expiry_date = datetime.fromisoformat(expiry_date_str + "T23:59:59+00:00")
                
                # Ensure timezone awareness for comparison
                if expiry_date.tzinfo is None:
                    expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                
                if expiry_date > datetime.now(timezone.utc):
                    discount_active = True
            except:
                pass
        
        product['discount_active'] = discount_active
        
        # Calculate discounted prices if discount is active
        if discount_active and discount_percentage:
            discounted_prices = []
            for price_item in product.get('prices', []):
                original_price = price_item['price']
                discounted_price = round(original_price * (1 - discount_percentage / 100), 2)
                discounted_prices.append({
                    **price_item,
                    'original_price': original_price,
                    'discounted_price': discounted_price
                })
            product['discounted_prices'] = discounted_prices
    
    return products

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get a single product by ID with discount calculation"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate discounted prices for the product
    discount_percentage = product.get('discount_percentage')
    discount_expiry = product.get('discount_expiry_date')
    
    # Check if discount is valid
    discount_active = False
    if discount_percentage and discount_expiry:
        try:
            # Parse the date string
            expiry_date_str = discount_expiry.replace('Z', '+00:00')
            if 'T' in expiry_date_str:
                expiry_date = datetime.fromisoformat(expiry_date_str)
            else:
                # If only date is provided (YYYY-MM-DD), add time and timezone
                expiry_date = datetime.fromisoformat(expiry_date_str + "T23:59:59+00:00")
            
            # Ensure timezone awareness for comparison
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
            
            if expiry_date > datetime.now(timezone.utc):
                discount_active = True
        except:
            pass
    
    product['discount_active'] = discount_active
    
    # Calculate discounted prices if discount is active
    if discount_active and discount_percentage:
        discounted_prices = []
        for price_item in product.get('prices', []):
            original_price = price_item['price']
            discounted_price = round(original_price * (1 - discount_percentage / 100), 2)
            discounted_prices.append({
                **price_item,
                'original_price': original_price,
                'discounted_price': discounted_price
            })
        product['discounted_prices'] = discounted_prices
    
    return product

@api_router.post("/products")
async def create_product(product: Product, current_user: dict = Depends(get_current_user)):
    """Create new product (Admin only)"""
    product_dict = product.model_dump()
    await db.products.insert_one(product_dict)
    product_dict.pop("_id", None)
    return {"message": "Product created successfully", "product": product_dict}

@api_router.put("/products/{product_id}")
async def update_product(product_id: str, product: Product, current_user: dict = Depends(get_current_user)):
    """Update product (Admin only)"""
    product_dict = product.model_dump()
    result = await db.products.update_one({"id": product_id}, {"$set": product_dict})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product updated successfully"}

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Delete product (Admin only)"""
    result = await db.products.delete_one({"id": product_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# ============= DISCOUNT APIS =============

@api_router.post("/admin/products/{product_id}/discount")
async def add_discount(product_id: str, discount: DiscountUpdate, current_user: dict = Depends(get_current_user)):
    """Add or update discount for a product (Admin only)"""
    # Validate discount percentage
    if discount.discount_percentage < 0 or discount.discount_percentage > 70:
        raise HTTPException(status_code=400, detail="Discount must be between 0% and 70%")
    
    # Validate expiry date is in the future
    try:
        # Parse the date string
        expiry_date_str = discount.discount_expiry_date.replace('Z', '+00:00')
        if 'T' in expiry_date_str:
            expiry_date = datetime.fromisoformat(expiry_date_str)
        else:
            # If only date is provided (YYYY-MM-DD), add time and timezone
            expiry_date = datetime.fromisoformat(expiry_date_str + "T23:59:59+00:00")
        
        # Ensure timezone awareness for comparison
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        
        if expiry_date <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Expiry date must be in the future")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Update product
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "discount_percentage": discount.discount_percentage,
            "discount_expiry_date": discount.discount_expiry_date
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Discount added successfully"}

@api_router.delete("/admin/products/{product_id}/discount")
async def remove_discount(product_id: str, current_user: dict = Depends(get_current_user)):
    """Remove discount from a product (Admin only)"""
    result = await db.products.update_one(
        {"id": product_id},
        {"$unset": {"discount_percentage": "", "discount_expiry_date": ""}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Discount removed successfully"}

@api_router.get("/admin/products/discounts")
async def get_products_with_discounts(current_user: dict = Depends(get_current_user)):
    """Get all products with discount information (Admin only)"""
    products = await db.products.find({}, {"_id": 0}).to_list(1000)
    return products

# ============= INVENTORY MANAGEMENT APIS =============

@api_router.put("/admin/products/{product_id}/inventory")
async def update_inventory(product_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update product inventory (Admin only)"""
    inventory_count = data.get("inventory_count")
    
    if inventory_count is None:
        raise HTTPException(status_code=400, detail="inventory_count is required")
    
    if inventory_count < 0:
        raise HTTPException(status_code=400, detail="Inventory count cannot be negative")
    
    update_data = {
        "inventory_count": inventory_count,
        "out_of_stock": inventory_count == 0
    }
    
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Inventory updated successfully"}

@api_router.get("/admin/products/{product_id}/stock-status")
async def get_stock_status(product_id: str, current_user: dict = Depends(get_current_user)):
    """Get product stock status (Admin only)"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0, "out_of_stock": 1, "inventory_count": 1})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "out_of_stock": product.get("out_of_stock", False),
        "inventory_count": product.get("inventory_count")
    }

@api_router.put("/admin/products/{product_id}/stock-status")
async def toggle_stock_status(product_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Toggle out of stock status (Admin only)"""
    out_of_stock = data.get("out_of_stock", False)
    
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {"out_of_stock": out_of_stock}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Stock status updated successfully"}

@api_router.put("/admin/products/{product_id}/available-cities")
async def update_available_cities(product_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update product available cities (Admin only)"""
    available_cities = data.get("available_cities", [])
    
    # Validate available_cities is a list
    if not isinstance(available_cities, list):
        raise HTTPException(status_code=400, detail="available_cities must be an array")
    
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {"available_cities": available_cities if available_cities else None}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Available cities updated successfully"}

# ============= BEST SELLER APIS =============

@api_router.post("/admin/best-sellers")
async def update_best_sellers(data: dict, current_user: dict = Depends(get_current_user)):
    """Bulk update best sellers (Admin only)"""
    product_ids = data.get("product_ids", [])
    
    # Remove best seller flag from all products
    await db.products.update_many({}, {"$set": {"isBestSeller": False}})
    
    # Set best seller flag for selected products
    if product_ids:
        await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"isBestSeller": True}}
        )
    
    return {"message": "Best sellers updated successfully"}

@api_router.get("/admin/best-sellers")
async def get_best_sellers(current_user: dict = Depends(get_current_user)):
    """Get all best seller products (Admin only)"""
    products = await db.products.find({"isBestSeller": True}, {"_id": 0}).to_list(1000)
    return products

# ============= FESTIVAL PRODUCT APIS =============

@api_router.post("/admin/festival-product")
async def set_festival_product(data: dict, current_user: dict = Depends(get_current_user)):
    """Set festival product (Admin only)"""
    product_id = data.get("product_id")
    
    if product_id:
        # Store festival product ID in settings collection
        await db.settings.update_one(
            {"key": "festival_product"},
            {"$set": {"key": "festival_product", "product_id": product_id}},
            upsert=True
        )
        return {"message": "Festival product set successfully"}
    else:
        # Remove festival product
        await db.settings.delete_one({"key": "festival_product"})
        return {"message": "Festival product removed successfully"}

@api_router.get("/admin/festival-product")
async def get_festival_product():
    """Get current festival product (Public API)"""
    setting = await db.settings.find_one({"key": "festival_product"}, {"_id": 0})
    
    if not setting:
        return None
    
    product_id = setting.get("product_id")
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    return product

# ============= FESTIVAL PRODUCTS (BULK SELECTION LIKE BEST SELLERS) =============

@api_router.post("/admin/festival-products")
async def update_festival_products(data: dict, current_user: dict = Depends(get_current_user)):
    """Bulk update festival products (Admin only) - Similar to best sellers"""
    product_ids = data.get("product_ids", [])
    
    # Remove festival flag from all products
    await db.products.update_many({}, {"$set": {"isFestival": False}})
    
    # Set festival flag for selected products
    if product_ids:
        await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"isFestival": True}}
        )
    
    return {"message": "Festival products updated successfully"}

@api_router.get("/admin/festival-products")
async def get_festival_products(current_user: dict = Depends(get_current_user)):
    """Get all festival products (Admin only)"""
    products = await db.products.find({"isFestival": True}, {"_id": 0}).to_list(1000)
    return products

@api_router.put("/admin/products/{product_id}/festival")
async def toggle_product_festival(product_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Toggle festival status for a single product (Admin only)"""
    is_festival = data.get("isFestival", False)
    
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {"isFestival": is_festival}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": f"Product festival status updated to {is_festival}"}

# ============= FREE DELIVERY SETTINGS API =============

@api_router.post("/admin/settings/free-delivery")
async def set_free_delivery_threshold(data: dict, current_user: dict = Depends(get_current_user)):
    """Set free delivery threshold (Admin only)"""
    # Verify admin access
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    threshold = data.get("threshold", 0)
    enabled = data.get("enabled", False)
    
    await db.settings.update_one(
        {"key": "free_delivery"},
        {"$set": {"key": "free_delivery", "threshold": float(threshold), "enabled": bool(enabled)}},
        upsert=True
    )
    return {"message": "Free delivery settings updated successfully", "threshold": threshold, "enabled": enabled}

@api_router.get("/settings/free-delivery")
async def get_free_delivery_settings():
    """Get free delivery settings (Public API)"""
    setting = await db.settings.find_one({"key": "free_delivery"}, {"_id": 0})
    
    if not setting:
        # Default: Free delivery enabled for orders >= Rs.1000
        return {"enabled": True, "threshold": 1000}
    
    return {"enabled": setting.get("enabled", True), "threshold": setting.get("threshold", 1000)}

# ============= IMAGE UPLOAD API =============

@api_router.post("/upload/image")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload product image from desktop"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create uploads directory if not exists
        uploads_dir = ROOT_DIR.parent / "frontend" / "public" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = uploads_dir / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Return URL
        image_url = f"/uploads/{filename}"
        return {"url": image_url, "message": "Image uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

# Alias for frontend compatibility
@api_router.post("/upload-image")
async def upload_image_alias(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload product image from desktop (alias endpoint)"""
    return await upload_image(file, current_user)

# ============= ORDERS APIS =============

@api_router.post("/orders")
async def create_order(order_data: OrderCreate, current_user: dict = Depends(get_current_user_optional)):
    """Create new order - allows guest checkout"""
    try:
        print(f"DEBUG: Received order data: {order_data.model_dump()}")
        print(f"DEBUG: Current user: {current_user}")
        
        # Check city availability and inventory for all items
        unavailable_products = []
        for item in order_data.items:
            product = await db.products.find_one({"id": item.product_id})
            if product:
                # Check if product is available for delivery to the customer's city
                available_cities = product.get("available_cities")
                if available_cities and len(available_cities) > 0:
                    # If available_cities is set and not empty, check if the city is in the list
                    if order_data.city not in available_cities:
                        unavailable_products.append(item.name)
                        continue
                
                if product.get("out_of_stock", False):
                    raise HTTPException(status_code=400, detail=f"Product {item.name} is out of stock")
                
                inventory_count = product.get("inventory_count")
                if inventory_count is not None and inventory_count < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient inventory for {item.name}")
        
        # If any products are not available for delivery to this city, return error
        if unavailable_products:
            products_list = ", ".join(unavailable_products)
            raise HTTPException(
                status_code=400, 
                detail=f"The following products are not available for delivery to {order_data.city}: {products_list}"
            )
        
        # Generate order ID and tracking code
        order_id = generate_order_id()
        tracking_code = generate_tracking_code()
        
        # Use city as location if location is not provided
        location_value = order_data.location or order_data.city or ""
        
        # Check if this is a custom location
        is_custom_location = order_data.is_custom_location or False
        custom_city = order_data.custom_city
        custom_state = order_data.custom_state
        
        # Detect if this is a custom city request (city not in our delivery locations)
        custom_city_request = False
        if not is_custom_location and order_data.city and order_data.state:
            # Check if city exists by matching both city name AND state (CASE-INSENSITIVE)
            city_exists = await db.locations.find_one({
                "name": {"$regex": f"^{order_data.city}$", "$options": "i"},
                "state": {"$regex": f"^{order_data.state}$", "$options": "i"}
            })
            if not city_exists:
                custom_city_request = True
                print(f"🆕 CUSTOM CITY REQUEST: {order_data.city}, {order_data.state} - Awaiting approval")
            else:
                print(f"✅ EXISTING CITY CONFIRMED: {order_data.city}, {order_data.state}")
        
        # SERVER-SIDE DELIVERY CHARGE CALCULATION
        # For custom locations or custom city requests, delivery charge is 0 initially
        calculated_delivery_charge = 0.0
        
        if is_custom_location or custom_city_request:
            # Custom city - delivery charge will be calculated by admin
            calculated_delivery_charge = 0.0
            if custom_city_request:
                print(f"📍 CUSTOM CITY REQUEST: {order_data.city}, {order_data.state} - Delivery charge to be determined after approval")
            else:
                print(f"📍 CUSTOM LOCATION: {custom_city}, {custom_state} - Delivery charge to be calculated by admin")
        else:
            # Find the city's delivery settings from database
            # Match by both city name AND state for accuracy (CASE-INSENSITIVE)
            city_location = await db.locations.find_one({
                "name": {"$regex": f"^{order_data.city}$", "$options": "i"},
                "state": {"$regex": f"^{order_data.state}$", "$options": "i"}
            })
            
            if city_location:
                base_charge = city_location.get("charge", 99.0)
                free_delivery_threshold = city_location.get("free_delivery_threshold") or 0
                
                # Check if order qualifies for free delivery (threshold must be > 0)
                if free_delivery_threshold and free_delivery_threshold > 0 and order_data.subtotal >= free_delivery_threshold:
                    calculated_delivery_charge = 0.0
                    print(f"🎁 FREE DELIVERY APPLIED: {order_data.city} - Subtotal Rs.{order_data.subtotal} >= Threshold Rs.{free_delivery_threshold}")
                else:
                    calculated_delivery_charge = base_charge
                    print(f"💰 DELIVERY CHARGE APPLIED: {order_data.city} - Rs.{base_charge}")
            else:
                # City not found in database, treat as custom city request
                # This should ONLY happen for truly non-existent cities
                custom_city_request = True
                calculated_delivery_charge = 0.0
                print(f"⚠️ CITY NOT IN DATABASE: {order_data.city}, {order_data.state} - Treating as custom city request")
                print(f"📝 Debug: Please verify city name and state spelling match the database")
        
        # Calculate correct total
        calculated_total = order_data.subtotal + calculated_delivery_charge
        
        # Determine payment status and order status
        # For custom city requests or online payments, status is pending until verified
        payment_status = "pending"
        order_status = "pending" if custom_city_request else "pending"  # All orders start as pending until payment verified
        
        # Create order with SERVER-CALCULATED values
        order = {
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "tracking_code": tracking_code,
            "user_id": current_user["id"],
            "customer_name": order_data.customer_name,
            "email": order_data.email,
            "phone": order_data.phone,
            "whatsapp_number": order_data.whatsapp_number,
            "address": order_data.address,
            "doorNo": order_data.doorNo,
            "building": order_data.building,
            "street": order_data.street,
            "city": order_data.city,
            "state": order_data.state,
            "pincode": order_data.pincode,
            "location": location_value,
            "items": [item.model_dump() for item in order_data.items],
            "subtotal": order_data.subtotal,
            "delivery_charge": calculated_delivery_charge,
            "total": calculated_total,
            "payment_method": order_data.payment_method,
            "payment_sub_method": order_data.payment_sub_method,
            "payment_status": payment_status,
            "order_status": order_status,
            "custom_city_request": custom_city_request,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "estimated_delivery": (datetime.now(timezone.utc)).isoformat(),
            "admin_notes": None,
            "delivery_days": None,
            "cancelled": False,
            "cancelled_at": None,
            "cancel_reason": None,
            "cancellation_fee": 0.0,
            "is_custom_location": is_custom_location,
            "custom_city": custom_city,
            "custom_state": custom_state,
            "distance_from_guntur": order_data.distance_from_guntur if hasattr(order_data, 'distance_from_guntur') else None
        }
        
        # If custom city request, create a city suggestion entry
        if custom_city_request:
            suggestion_id = str(uuid.uuid4())
            city_suggestion = {
                "id": suggestion_id,
                "city": order_data.city,
                "state": order_data.state,
                "customer_name": order_data.customer_name,
                "phone": order_data.phone,
                "email": order_data.email,
                "status": "pending",
                "order_id": order_id,
                "created_at": datetime.now(timezone.utc)
            }
            await db.city_suggestions.insert_one(city_suggestion)
            print(f"📝 City suggestion created: {suggestion_id} for {order_data.city}, {order_data.state}")
        
        await db.orders.insert_one(order)
        
        # Update inventory for each item
        for item in order_data.items:
            product = await db.products.find_one({"id": item.product_id})
            if product and product.get("inventory_count") is not None:
                new_count = product["inventory_count"] - item.quantity
                update_data = {"inventory_count": max(0, new_count)}
                
                # Mark as out of stock if inventory reaches 0
                if new_count <= 0:
                    update_data["out_of_stock"] = True
                
                await db.products.update_one(
                    {"id": item.product_id},
                    {"$set": update_data}
                )
        
        # Save user details for future orders
        saved_details = {
            "identifier": order_data.phone,  # Use phone as primary identifier
            "customer_name": order_data.customer_name,
            "email": order_data.email,
            "phone": order_data.phone,
            "doorNo": order_data.doorNo,
            "building": order_data.building,
            "street": order_data.street,
            "city": order_data.city,
            "state": order_data.state,
            "pincode": order_data.pincode,
            "location": location_value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.saved_user_details.update_one(
            {"identifier": order_data.phone},
            {"$set": saved_details},
            upsert=True
        )
        
        # Also save with email as identifier
        await db.saved_user_details.update_one(
            {"identifier": order_data.email},
            {"$set": {**saved_details, "identifier": order_data.email}},
            upsert=True
        )
        
        # Prepare email content
        items_list = []
        for item in order_data.items:
            items_list.append({
                "name": item.name,
                "weight": item.weight,
                "quantity": item.quantity,
                "price": item.price
            })
        
        email_data = {
            "order_id": order_id,
            "tracking_code": tracking_code,
            "customer_name": order_data.customer_name,
            "order_date": datetime.now().strftime("%B %d, %Y"),
            "total": calculated_total,
            "address": order_data.address,
            "doorNo": order_data.doorNo,
            "building": order_data.building,
            "street": order_data.street,
            "city": order_data.city,
            "state": order_data.state,
            "pincode": order_data.pincode,
            "location": order_data.location,
            "phone": order_data.phone,
            "items": items_list
        }
        
        # Send order confirmation email immediately when order is created
        # Customer will receive confirmation that order has been placed
        if order_data.email:
            try:
                email_sent = await send_order_confirmation_email_gmail(order_data.email, {**email_data, "order_status": order_status, "payment_status": payment_status})
                if email_sent:
                    logger.info(f"✅ Order confirmation email sent successfully to {order_data.email} for order {order_id}")
                else:
                    logger.warning(f"⚠️ Order confirmation email failed for {order_data.email}")
            except Exception as email_error:
                logger.error(f"❌ Failed to send order confirmation email: {str(email_error)}")
        
        # Remove MongoDB _id field before returning
        order.pop("_id", None)
        
        return {
            "message": "Order created successfully" + (" - Awaiting city approval" if custom_city_request else ""),
            "order_id": order_id,
            "tracking_code": tracking_code,
            "subtotal": order_data.subtotal,
            "delivery_charge": calculated_delivery_charge,
            "total": calculated_total,
            "custom_city_request": custom_city_request,
            "payment_required": custom_city_request,
            "order": order
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error creating order: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@api_router.get("/orders/track/{identifier}")
async def track_order(identifier: str):
    """Track order by order_id, tracking_code, phone number, or email (public API)"""
    # Check if identifier is order_id or tracking_code (return single order)
    order = await db.orders.find_one(
        {"$or": [
            {"order_id": identifier}, 
            {"tracking_code": identifier}
        ]},
        {"_id": 0}
    )
    
    if order:
        return {"orders": [order], "total": 1}
    
    # If not found by order_id/tracking_code, search by phone or email (return all orders)
    orders = await db.orders.find(
        {"$or": [
            {"phone": identifier},
            {"email": identifier}
        ]},
        {"_id": 0}
    ).sort("order_date", -1).to_list(length=100)  # Sort by newest first, limit 100
    
    if not orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"orders": orders, "total": len(orders)}

# ============= RAZORPAY PAYMENT APIS =============

@api_router.post("/payment/create-razorpay-order")
async def create_razorpay_order(data: dict):
    """Create Razorpay order for payment"""
    try:
        amount = data.get("amount")  # Amount in rupees
        currency = data.get("currency", "INR")
        receipt = data.get("receipt", f"order_{uuid.uuid4().hex[:12]}")
        
        if not amount:
            raise HTTPException(status_code=400, detail="Amount is required")
        
        # Convert amount to paise (Razorpay requires amount in smallest currency unit)
        amount_in_paise = int(float(amount) * 100)
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1  # Auto capture payment
        })
        
        logger.info(f"Razorpay order created: {razorpay_order['id']}")
        
        return {
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key_id": os.environ.get('RAZORPAY_KEY_ID', '')
        }
    
    except Exception as e:
        logger.error(f"Error creating Razorpay order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment order: {str(e)}")

@api_router.post("/payment/verify-razorpay-payment")
async def verify_razorpay_payment(data: dict):
    """Verify Razorpay payment signature"""
    try:
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        order_id = data.get("order_id")
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, order_id]):
            raise HTTPException(status_code=400, detail="Missing required payment verification fields")
        
        # Verify signature
        generated_signature = hmac.new(
            os.environ.get('RAZORPAY_KEY_SECRET', '').encode('utf-8'),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            logger.error(f"Payment signature verification failed for order {order_id}")
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Update order payment status and order status
        result = await db.orders.update_one(
            {"order_id": order_id},
            {"$set": {
                "payment_status": "completed",
                "order_status": "confirmed",
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "payment_verified_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get updated order
        order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
        
        # Send confirmation email
        if order and order.get("email"):
            try:
                send_order_confirmation_email_gmail(order)
                logger.info(f"Order confirmation email sent to {order.get('email')} for order {order_id}")
            except Exception as email_error:
                logger.error(f"Failed to send confirmation email: {str(email_error)}")
        
        logger.info(f"Payment verified and order {order_id} updated successfully")
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "order_id": order_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {str(e)}")

@api_router.get("/orders/user/{user_id}")
async def get_user_orders(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get all orders for a user"""
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    orders = await db.orders.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return orders

@api_router.get("/orders")
async def get_all_orders(current_user: dict = Depends(get_current_user)):
    """Get all orders (Admin only)"""
    orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return orders

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update order status (Admin only)"""
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    # Get the order before updating to get old status and email
    order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order.get("order_status", "")
    
    result = await db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"order_status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Send email notification if status changed and email exists
    if old_status != status and order.get("email"):
        try:
            logger.info(f"Attempting to send order status update email to {order.get('email')} for order {order_id}")
            # Update order data with new status for email
            order["order_status"] = status
            email_sent = await send_order_status_update_email(order["email"], order, old_status, status)
            if email_sent:
                logger.info(f"✅ Order status update email sent successfully to {order.get('email')}")
            else:
                logger.warning(f"⚠️ Order status update email function returned False for {order.get('email')}")
        except Exception as e:
            logger.error(f"❌ Failed to send order status update email: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't fail the request if email fails
    
    return {"message": "Order status updated successfully"}

@api_router.put("/orders/{order_id}/cancel")
async def cancel_order(order_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Cancel order (Admin only)"""
    cancel_reason = data.get("cancel_reason", "")
    
    result = await db.orders.update_one(
        {"order_id": order_id},
        {"$set": {
            "cancelled": True,
            "cancel_reason": cancel_reason,
            "order_status": "cancelled"
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order cancelled successfully"}

@api_router.post("/orders/{order_id}/cancel-customer")
async def cancel_order_customer(order_id: str, data: dict):
    """Cancel order by customer (20-minute window, Rs.20 fee)"""
    try:
        # Get the order
        order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if already cancelled
        if order.get("cancelled", False):
            raise HTTPException(status_code=400, detail="Order is already cancelled")
        
        # Check if order status allows cancellation
        if order.get("order_status") in ["delivered", "shipped"]:
            raise HTTPException(status_code=400, detail="Cannot cancel order that is already delivered or shipped")
        
        # Check 20-minute window
        created_at = order.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        time_diff = datetime.now(timezone.utc) - created_at
        minutes_passed = time_diff.total_seconds() / 60
        
        if minutes_passed > 20:
            raise HTTPException(
                status_code=400, 
                detail="Cancellation window expired. Orders can only be cancelled within 20 minutes of placement."
            )
        
        cancel_reason = data.get("cancel_reason", "Customer requested cancellation")
        
        # Update order with cancellation info
        result = await db.orders.update_one(
            {"order_id": order_id},
            {"$set": {
                "cancelled": True,
                "cancelled_at": datetime.now(timezone.utc),
                "cancel_reason": cancel_reason,
                "order_status": "cancelled",
                "cancellation_fee": 20.0
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Send cancellation email
        if order.get("email"):
            try:
                # Import email function if needed
                from gmail_service import send_order_cancellation_email
                await send_order_cancellation_email(order["email"], order, cancellation_fee=20.0)
            except Exception as e:
                logger.error(f"Failed to send cancellation email: {str(e)}")
        
        return {
            "message": "Order cancelled successfully",
            "cancellation_fee": 20.0,
            "refund_amount": order.get("total", 0) - 20.0 if order.get("payment_status") == "completed" else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

@api_router.post("/orders/{order_id}/complete-payment")
async def complete_payment(order_id: str, data: dict):
    """Complete payment for pending orders (for custom city requests after approval)"""
    try:
        # Get the order
        order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if order is cancelled
        if order.get("cancelled", False):
            raise HTTPException(status_code=400, detail="Cannot complete payment for cancelled order")
        
        # Check if payment is already completed
        if order.get("payment_status") == "completed":
            raise HTTPException(status_code=400, detail="Payment is already completed")
        
        # Get payment details from request
        payment_method = data.get("payment_method", order.get("payment_method", "online"))
        payment_sub_method = data.get("payment_sub_method", order.get("payment_sub_method"))
        
        # Update order with payment completion
        result = await db.orders.update_one(
            {"order_id": order_id},
            {"$set": {
                "payment_status": "completed",
                "payment_method": payment_method,
                "payment_sub_method": payment_sub_method,
                "order_status": "confirmed"
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Send payment confirmation email
        if order.get("email"):
            try:
                from gmail_service import send_payment_completion_email
                await send_payment_completion_email(order["email"], order)
            except Exception as e:
                logger.error(f"Failed to send payment completion email: {str(e)}")
        
        return {
            "message": "Payment completed successfully",
            "order_status": "confirmed",
            "tracking_code": order.get("tracking_code")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete payment: {str(e)}")


@api_router.post("/orders/{order_id}/payment-cancel")
async def cancel_order_payment(order_id: str, data: dict = {}):
    """Cancel order immediately when payment is cancelled (no auth required)"""
    try:
        # Get the order
        order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Only allow cancellation if payment is still pending
        if order.get("payment_status") != "pending":
            raise HTTPException(status_code=400, detail="Cannot cancel order with non-pending payment")
        
        cancel_reason = data.get("cancel_reason", "Payment cancelled by customer")
        
        # Update order to cancelled status
        result = await db.orders.update_one(
            {"order_id": order_id},
            {"$set": {
                "cancelled": True,
                "cancel_reason": cancel_reason,
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "order_status": "cancelled",
                "payment_status": "cancelled"
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        logger.info(f"🚫 ORDER CANCELLED: {order_id} - Reason: {cancel_reason}")
        
        # Send cancellation email
        if order.get("email"):
            try:
                from gmail_service import send_order_cancellation_email
                email_sent = await send_order_cancellation_email(order.get("email"), order, cancel_reason)
                if email_sent:
                    logger.info(f"✅ Cancellation email sent successfully to {order.get('email')} for order {order_id}")
                else:
                    logger.warning(f"⚠️ Cancellation email failed for {order.get('email')}")
            except Exception as email_error:
                logger.error(f"❌ Failed to send cancellation email: {str(email_error)}")
        
        return {"message": "Order cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

@api_router.put("/orders/{order_id}/admin-update")
async def update_order_admin_fields(order_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """Update admin fields like notes and delivery days"""
    update_fields = {}
    
    if "admin_notes" in data:
        update_fields["admin_notes"] = data["admin_notes"]
    if "delivery_days" in data:
        update_fields["delivery_days"] = data["delivery_days"]
    if "order_status" in data:
        update_fields["order_status"] = data["order_status"]
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Get the order before updating to get old status and email
    order = await db.orders.find_one({"order_id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order.get("order_status", "")
    
    result = await db.orders.update_one(
        {"order_id": order_id},
        {"$set": update_fields}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Send email notification if order status was changed and email exists
    if "order_status" in update_fields and old_status != update_fields["order_status"] and order.get("email"):
        try:
            logger.info(f"Attempting to send order status update email to {order.get('email')} for order {order_id}")
            # Update order data with new status for email
            order["order_status"] = update_fields["order_status"]
            email_sent = await send_order_status_update_email(order["email"], order, old_status, update_fields["order_status"])
            if email_sent:
                logger.info(f"✅ Order status update email sent successfully to {order.get('email')}")
            else:
                logger.warning(f"⚠️ Order status update email function returned False for {order.get('email')}")
        except Exception as e:
            logger.error(f"❌ Failed to send order status update email: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't fail the request if email fails
    
    return {"message": "Order updated successfully"}

@api_router.get("/orders/analytics/summary")
async def get_orders_analytics(current_user: dict = Depends(get_current_user)):
    """Get order analytics and statistics"""
    try:
        # Get all orders
        all_orders = await db.orders.find({}, {"_id": 0}).to_list(10000)
        
        # Filter out cancelled orders for sales calculations
        non_cancelled_orders = [o for o in all_orders if not o.get("cancelled", False) and o.get("order_status") != "cancelled"]
        
        # Calculate statistics
        total_orders = len(all_orders)
        # Only sum sales from non-cancelled orders
        total_sales = sum(order.get("total", 0) for order in non_cancelled_orders)
        active_orders = len([o for o in non_cancelled_orders if o.get("order_status") != "delivered"])
        cancelled_orders = len([o for o in all_orders if o.get("cancelled", False) or o.get("order_status") == "cancelled"])
        completed_orders = len([o for o in non_cancelled_orders if o.get("order_status") == "delivered"])
        
        # Monthly sales - only include non-cancelled orders
        from collections import defaultdict
        monthly_sales = defaultdict(float)
        monthly_orders = defaultdict(int)
        
        for order in non_cancelled_orders:
            created_at = order.get("created_at", "")
            if created_at:
                try:
                    order_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    month_key = order_date.strftime("%Y-%m")
                    monthly_sales[month_key] += order.get("total", 0)
                    monthly_orders[month_key] += 1
                except:
                    pass
        
        # Top products - only include non-cancelled orders
        product_counts = defaultdict(int)
        for order in non_cancelled_orders:
            for item in order.get("items", []):
                product_counts[item.get("name", "Unknown")] += item.get("quantity", 0)
        
        top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_orders": total_orders,
            "total_sales": total_sales,
            "active_orders": active_orders,
            "cancelled_orders": cancelled_orders,
            "completed_orders": completed_orders,
            "monthly_sales": dict(monthly_sales),
            "monthly_orders": dict(monthly_orders),
            "top_products": [{"name": name, "count": count} for name, count in top_products]
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# ============= USER DETAILS API =============

@api_router.get("/user-details/{identifier}")
async def get_user_details(identifier: str):
    """Get user details by phone or email from most recent order"""
    # Search for the most recent order with this phone or email
    order = await db.orders.find_one(
        {"$or": [
            {"phone": identifier},
            {"email": identifier}
        ]},
        {"_id": 0},
        sort=[("created_at", -1)]  # Get most recent order
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="No details found")
    
    # Return relevant customer details
    return {
        "customer_name": order.get("customer_name"),
        "email": order.get("email"),
        "phone": order.get("phone"),
        "doorNo": order.get("doorNo"),
        "building": order.get("building"),
        "street": order.get("street"),
        "city": order.get("city"),
        "state": order.get("state"),
        "pincode": order.get("pincode"),
        "location": order.get("location")
    }

# ============= LOCATIONS API =============

@api_router.get("/locations")
async def get_locations():
    """Get delivery locations with state information"""
    # Check if custom locations exist in database
    locations = await db.locations.find({}, {"_id": 0}).to_list(1000)
    
    if not locations:
        # Return default cities with charges and state information
        locations = []
        
        # Add default cities with charges
        for city, charge in DEFAULT_DELIVERY_CHARGES.items():
            state = "Andhra Pradesh" if city in ANDHRA_PRADESH_CITIES else "Telangana"
            locations.append({"name": city, "charge": charge, "state": state})
        
        # Add remaining AP cities with default charge
        for city in ANDHRA_PRADESH_CITIES:
            if city not in DEFAULT_DELIVERY_CHARGES:
                locations.append({"name": city, "charge": DEFAULT_OTHER_CITY_CHARGE, "state": "Andhra Pradesh"})
        
        # Add remaining Telangana cities with default charge
        for city in TELANGANA_CITIES:
            if city not in DEFAULT_DELIVERY_CHARGES:
                locations.append({"name": city, "charge": DEFAULT_OTHER_CITY_CHARGE, "state": "Telangana"})
    else:
        # For database locations, add state information if not present
        for loc in locations:
            if "state" not in loc or not loc["state"]:
                # Determine state based on city name
                city_name = loc["name"]
                if city_name in ANDHRA_PRADESH_CITIES:
                    loc["state"] = "Andhra Pradesh"
                elif city_name in TELANGANA_CITIES:
                    loc["state"] = "Telangana"
                else:
                    loc["state"] = "Andhra Pradesh"  # Default
    
    return locations

@api_router.post("/admin/locations")
async def update_locations(locations: List[Location], current_user: dict = Depends(get_current_user)):
    """Update delivery locations (Admin only)"""
    # Clear existing locations
    await db.locations.delete_many({})
    
    # Insert new locations
    if locations:
        location_dicts = [loc.model_dump() for loc in locations]
        await db.locations.insert_many(location_dicts)
    
    return {"message": "Locations updated successfully"}

@api_router.put("/admin/locations/{city_name}")
async def update_city_settings(
    city_name: str, 
    charge: Optional[float] = None,
    free_delivery_threshold: Optional[float] = None,
    state: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update city delivery settings including charge and free delivery threshold"""
    
    # Check if city exists in database
    existing = await db.locations.find_one({"name": city_name})
    
    if existing:
        # Update existing city
        update_data = {}
        if charge is not None:
            update_data["charge"] = charge
        if free_delivery_threshold is not None:
            update_data["free_delivery_threshold"] = free_delivery_threshold
        if state is not None:
            update_data["state"] = state
        
        if update_data:
            await db.locations.update_one({"name": city_name}, {"$set": update_data})
    else:
        # Create new city entry
        city_data = {"name": city_name}
        if charge is not None:
            city_data["charge"] = charge
        if free_delivery_threshold is not None:
            city_data["free_delivery_threshold"] = free_delivery_threshold
        
        # Determine state - use provided state or auto-detect
        if state:
            city_data["state"] = state
        elif city_name in ANDHRA_PRADESH_CITIES:
            city_data["state"] = "Andhra Pradesh"
        elif city_name in TELANGANA_CITIES:
            city_data["state"] = "Telangana"
        else:
            city_data["state"] = "Andhra Pradesh"
        
        await db.locations.insert_one(city_data)
    
    return {"message": f"Settings updated for {city_name}"}

@api_router.delete("/admin/locations/{city_name}")
async def delete_location(city_name: str, current_user: dict = Depends(get_current_user)):
    """Delete a delivery location (Admin only)"""
    result = await db.locations.delete_one({"name": city_name})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return {"message": f"Location '{city_name}' deleted successfully"}

# ============= CUSTOM CITY API =============

@api_router.post("/calculate-custom-city-delivery")
async def calculate_custom_city_delivery(data: dict):
    """Calculate delivery charge for a custom city not in the delivery list"""
    from distance_calculator import calculate_delivery_charge_for_custom_city
    
    city_name = data.get("city_name")
    state_name = data.get("state_name")
    
    if not city_name or not state_name:
        raise HTTPException(status_code=400, detail="City name and state name are required")
    
    # Calculate delivery charge and distance
    charge, distance, coords = calculate_delivery_charge_for_custom_city(city_name, state_name)
    
    return {
        "city_name": city_name,
        "state_name": state_name,
        "delivery_charge": charge,
        "distance_from_guntur_km": distance,
        "coordinates": coords,
        "message": f"Estimated delivery charge based on {distance}km distance from Guntur" if distance else "Unable to calculate distance, using default charge"
    }

@api_router.get("/admin/pending-cities")
async def get_pending_cities(current_user: dict = Depends(get_current_user)):
    """Get all custom cities from orders that need admin approval"""
    # Find all orders with custom locations
    orders = await db.orders.find(
        {"is_custom_location": True},
        {"_id": 0, "custom_city": 1, "custom_state": 1, "distance_from_guntur": 1, "delivery_charge": 1, "created_at": 1}
    ).to_list(1000)
    
    # Get all existing locations to filter out already-approved cities
    existing_locations = await db.locations.find({}, {"_id": 0, "name": 1, "state": 1}).to_list(10000)
    existing_set = {f"{loc['name']}_{loc['state']}" for loc in existing_locations}
    
    # Group by city and state to remove duplicates
    cities_dict = {}
    for order in orders:
        city_name = order.get('custom_city', '')
        state_name = order.get('custom_state', '')
        city_key = f"{city_name}_{state_name}"
        
        # Skip if this city has already been approved (exists in locations)
        if city_key in existing_set:
            continue
            
        if city_key not in cities_dict:
            cities_dict[city_key] = {
                "city_name": city_name,
                "state_name": state_name,
                "distance_km": order.get("distance_from_guntur"),
                "suggested_charge": order.get("delivery_charge"),
                "first_order_date": order.get("created_at"),
                "order_count": 1
            }
        else:
            cities_dict[city_key]["order_count"] += 1
    
    return list(cities_dict.values())

@api_router.post("/admin/approve-city")
async def approve_custom_city(data: dict, current_user: dict = Depends(get_current_user)):
    """Approve a custom city and add it to delivery locations with admin-set charge"""
    city_name = data.get("city_name")
    state_name = data.get("state_name")
    delivery_charge = data.get("delivery_charge")
    free_delivery_threshold = data.get("free_delivery_threshold")
    
    if not city_name or not state_name or delivery_charge is None:
        raise HTTPException(status_code=400, detail="City name, state name, and delivery charge are required")
    
    # Check if city already exists
    existing = await db.locations.find_one({"name": city_name, "state": state_name})
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"City '{city_name}, {state_name}' has already been approved and is available for delivery. Please refresh the page to see updated pending cities."
        )
    
    # Add city to locations
    city_data = {
        "name": city_name,
        "state": state_name,
        "charge": delivery_charge
    }
    
    if free_delivery_threshold:
        city_data["free_delivery_threshold"] = free_delivery_threshold
    
    await db.locations.insert_one(city_data)
    
    # Check if there's a matching city suggestion and update its status + send email
    try:
        suggestion = await db.city_suggestions.find_one({
            "city": city_name,
            "state": state_name,
            "status": "pending"
        }, {"_id": 0})
        
        if suggestion:
            # Update suggestion status to approved
            await db.city_suggestions.update_one(
                {"id": suggestion["id"]},
                {"$set": {"status": "approved", "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Send approval email if customer provided email
            if suggestion.get("email"):
                try:
                    await send_city_approval_email(suggestion["email"], suggestion)
                    logger.info(f"City approval email sent to {suggestion['email']} for {city_name}, {state_name}")
                except Exception as e:
                    logger.error(f"Failed to send city approval email: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating city suggestion: {str(e)}")
        # Don't fail the approval if email/suggestion update fails
    
    # Remove _id field from city_data before returning to avoid serialization issues
    city_data.pop("_id", None)
    
    return {
        "message": f"City '{city_name}, {state_name}' approved and added to delivery locations",
        "city_data": city_data
    }

# ============= STATES API =============

@api_router.get("/states")
async def get_states():
    """Get available states"""
    # Check if custom states exist in database
    states = await db.states.find({}, {"_id": 0}).to_list(1000)
    
    if not states:
        # Return only AP and Telangana as default
        default_states = [
            {"name": "Andhra Pradesh", "enabled": True},
            {"name": "Telangana", "enabled": True}
        ]
        return default_states
    
    return states

@api_router.get("/admin/states")
async def get_admin_states(current_user: dict = Depends(get_current_user)):
    """Get all states for admin management"""
    states = await db.states.find({}, {"_id": 0}).to_list(1000)
    
    if not states:
        # Return only AP and Telangana as default
        default_states = [
            {"name": "Andhra Pradesh", "enabled": True},
            {"name": "Telangana", "enabled": True}
        ]
        return default_states
    
    return states

@api_router.post("/admin/states")
async def add_state(state: State, current_user: dict = Depends(get_current_user)):
    """Add a new state (Admin only)"""
    # Check if state already exists
    existing = await db.states.find_one({"name": state.name})
    if existing:
        raise HTTPException(status_code=400, detail="State already exists")
    
    await db.states.insert_one(state.model_dump())
    return {"message": f"State '{state.name}' added successfully"}

@api_router.put("/admin/states/{state_name}")
async def update_state(state_name: str, state: State, current_user: dict = Depends(get_current_user)):
    """Update state status (Admin only)"""
    result = await db.states.update_one(
        {"name": state_name},
        {"$set": {"enabled": state.enabled}}
    )
    
    if result.matched_count == 0:
        # If state doesn't exist, create it
        await db.states.insert_one({"name": state_name, "enabled": state.enabled})
    
    return {"message": f"State '{state_name}' updated successfully"}

@api_router.delete("/admin/states/{state_name}")
async def delete_state(state_name: str, current_user: dict = Depends(get_current_user)):
    """Delete a state (Admin only)"""
    result = await db.states.delete_one({"name": state_name})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="State not found")
    
    return {"message": f"State '{state_name}' deleted successfully"}


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# City Suggestion endpoint
@api_router.post("/suggest-city")
async def suggest_city(data: dict):
    """Handle city suggestion from customers"""
    try:
        suggestion = {
            "id": str(uuid.uuid4()),
            "state": data.get("state"),
            "city": data.get("city"),
            "customer_name": data.get("customer_name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }
        
        await db.city_suggestions.insert_one(suggestion)
        
        return {"message": "City suggestion received successfully", "suggestion_id": suggestion["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit city suggestion: {str(e)}")

# City Suggestions endpoint (alternative endpoint for checkout flow)
@api_router.post("/city-suggestions")
async def create_city_suggestion(data: dict):
    """Save city suggestion with contact info when customer searches for unlisted city"""
    try:
        suggestion = {
            "id": str(uuid.uuid4()),
            "state": data.get("state"),
            "city": data.get("city_name", data.get("city")),
            "customer_name": data.get("customer_name", ""),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }
        
        await db.city_suggestions.insert_one(suggestion)
        
        logger.info(f"City suggestion saved: {suggestion['city']} ({suggestion['state']}) - Contact: {suggestion['phone']}, {suggestion['email']}")
        
        return {"message": "City suggestion saved successfully", "suggestion_id": suggestion["id"]}
    except Exception as e:
        logger.error(f"Failed to save city suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save city suggestion: {str(e)}")

# ============= BUG REPORT ENDPOINTS =============

@api_router.post("/reports")
async def create_bug_report(
    email: str = Form(...),
    mobile: str = Form(...),
    issue_description: str = Form(...),
    photo: UploadFile = File(None)
):
    """Create a new bug report with optional photo"""
    try:
        photo_url = None
        
        # Save photo if provided
        if photo:
            photo_filename = f"bug_report_{uuid.uuid4()}_{photo.filename}"
            photo_path = f"/app/frontend/public/uploads/{photo_filename}"
            
            async with aiofiles.open(photo_path, "wb") as buffer:
                content = await photo.read()
                await buffer.write(content)
            
            photo_url = f"/uploads/{photo_filename}"
        
        bug_report = {
            "id": str(uuid.uuid4()),
            "email": email,
            "mobile": mobile,
            "issue_description": issue_description,
            "photo_url": photo_url,
            "status": "New",
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.bug_reports.insert_one(bug_report)
        
        return {
            "message": "Bug report submitted successfully! We'll look into it soon.",
            "report_id": bug_report["id"]
        }
    except Exception as e:
        logger.error(f"Error creating bug report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit bug report: {str(e)}")

@api_router.get("/admin/reports")
async def get_all_reports(current_user: dict = Depends(get_current_user)):
    """Get all bug reports (admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        reports = await db.bug_reports.find({}, {"_id": 0}).sort("created_at", -1).to_list(length=None)
        
        # Convert datetime to ISO string for JSON serialization
        for report in reports:
            if isinstance(report.get("created_at"), datetime):
                report["created_at"] = report["created_at"].isoformat()
        
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bug reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch bug reports: {str(e)}")

@api_router.put("/admin/reports/{report_id}/status")
async def update_report_status(
    report_id: str,
    status_update: BugReportStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update bug report status (admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Validate status
        valid_statuses = ["New", "In Progress", "Resolved"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        result = await db.bug_reports.update_one(
            {"id": report_id},
            {"$set": {"status": status_update.status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Bug report not found")
        
        return {"message": "Status updated successfully", "status": status_update.status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating report status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@api_router.delete("/admin/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a bug report (admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get report to delete photo if exists
        report = await db.bug_reports.find_one({"id": report_id}, {"_id": 0})
        
        if not report:
            raise HTTPException(status_code=404, detail="Bug report not found")
        
        # Delete photo file if exists
        if report.get("photo_url"):
            try:
                photo_path = f"/app/frontend/public{report['photo_url']}"
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except Exception as e:
                logger.warning(f"Failed to delete photo: {str(e)}")
        
        result = await db.bug_reports.delete_one({"id": report_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Bug report not found")
        
        return {"message": "Bug report deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

# ============= CITY SUGGESTION ENDPOINTS =============

@api_router.get("/admin/city-suggestions")
async def get_city_suggestions(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get city suggestions with optional status filter (admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Build query filter
        query = {}
        if status and status in ["pending", "approved", "rejected"]:
            query["status"] = status
        
        suggestions = await db.city_suggestions.find(
            query, 
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=None)
        
        # Convert datetime to ISO string for JSON serialization
        for suggestion in suggestions:
            if isinstance(suggestion.get("created_at"), datetime):
                suggestion["created_at"] = suggestion["created_at"].isoformat()
            if isinstance(suggestion.get("updated_at"), datetime):
                suggestion["updated_at"] = suggestion["updated_at"].isoformat()
        
        return suggestions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching city suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch city suggestions: {str(e)}")

@api_router.put("/admin/city-suggestions/{suggestion_id}/status")
async def update_city_suggestion_status(
    suggestion_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update city suggestion status (admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        status = data.get("status")
        if status not in ["pending", "approved", "rejected"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Get the suggestion before updating to send email
        suggestion = await db.city_suggestions.find_one({"id": suggestion_id}, {"_id": 0})
        if not suggestion:
            raise HTTPException(status_code=404, detail="City suggestion not found")
        
        # If approving, add city to locations collection (if delivery charge provided)
        if status == "approved":
            delivery_charge = data.get("delivery_charge")
            free_delivery_threshold = data.get("free_delivery_threshold")
            
            # Check if city already exists in locations
            existing = await db.locations.find_one({
                "name": suggestion.get("city"),
                "state": suggestion.get("state")
            })
            
            # Only add to locations if it doesn't exist and delivery charge is provided
            if not existing and delivery_charge is not None:
                city_data = {
                    "name": suggestion.get("city"),
                    "state": suggestion.get("state"),
                    "charge": delivery_charge
                }
                
                if free_delivery_threshold:
                    city_data["free_delivery_threshold"] = free_delivery_threshold
                
                await db.locations.insert_one(city_data)
                logger.info(f"City {suggestion.get('city')}, {suggestion.get('state')} added to locations with charge Rs.{delivery_charge}")
        
        # Update suggestion status
        result = await db.city_suggestions.update_one(
            {"id": suggestion_id},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="City suggestion not found")
        
        # Send email notifications based on status
        if suggestion.get("email"):
            try:
                if status == "approved":
                    await send_city_approval_email(suggestion["email"], suggestion)
                    logger.info(f"City approval email sent to {suggestion['email']} for {suggestion.get('city')}, {suggestion.get('state')}")
                elif status == "rejected":
                    await send_city_rejection_email(suggestion["email"], suggestion)
                    logger.info(f"City rejection email sent to {suggestion['email']} for {suggestion.get('city')}, {suggestion.get('state')}")
            except Exception as e:
                logger.error(f"Failed to send city status email: {str(e)}")
                # Don't fail the request if email fails
        
        return {"message": "City suggestion status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating city suggestion status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@api_router.delete("/admin/city-suggestions/{suggestion_id}")
async def delete_city_suggestion(
    suggestion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a city suggestion (admin only) - only approved or rejected suggestions can be deleted"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if suggestion exists and get its status
        suggestion = await db.city_suggestions.find_one({"id": suggestion_id}, {"_id": 0})
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="City suggestion not found")
        
        # Prevent deleting pending suggestions
        if suggestion.get("status") == "pending":
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete pending suggestions. Please approve or reject first."
            )
        
        # Delete the suggestion
        result = await db.city_suggestions.delete_one({"id": suggestion_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="City suggestion not found")
        
        logger.info(f"City suggestion deleted: {suggestion.get('city')}, {suggestion.get('state')} (Status: {suggestion.get('status')})")
        return {"message": "City suggestion deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting city suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete city suggestion: {str(e)}")

# ============= NOTIFICATION ENDPOINTS =============

@api_router.get("/admin/notifications/count")
async def get_notification_count(current_user: dict = Depends(get_current_user)):
    """Get count of pending notifications (admin only) - excludes recently dismissed"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admin_id = current_user.get("id")
        
        # Get recent dismissals (within last 5 minutes) for each type
        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        dismissed_types = set()
        recent_dismissals = await db.dismissed_notifications.find({
            "admin_id": admin_id,
            "dismissed_at": {"$gte": five_minutes_ago}
        }).to_list(100)
        
        for dismissal in recent_dismissals:
            dismissed_types.add(dismissal.get("type"))
        
        # Count pending bug reports (status = 'New' or 'In Progress')
        bug_reports_count = 0
        if "bug_reports" not in dismissed_types:
            bug_reports_count = await db.bug_reports.count_documents({
                "status": {"$in": ["New", "In Progress"]}
            })
        
        # Count pending city suggestions
        city_suggestions_count = 0
        if "city_suggestions" not in dismissed_types:
            city_suggestions_count = await db.city_suggestions.count_documents({
                "status": "pending"
            })
        
        # Count orders from last 24 hours (new orders)
        new_orders_count = 0
        if "new_orders" not in dismissed_types:
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            new_orders_count = await db.orders.count_documents({
                "created_at": {"$gte": yesterday}
            })
        
        return {
            "bug_reports": bug_reports_count,
            "city_suggestions": city_suggestions_count,
            "new_orders": new_orders_count,
            "total": bug_reports_count + city_suggestions_count + new_orders_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notification count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch notification count: {str(e)}")


@api_router.post("/admin/notifications/mark-read")
async def mark_notification_read(data: dict, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        notification_type = data.get("type")
        notification_id = data.get("id")
        
        if not notification_type:
            raise HTTPException(status_code=400, detail="Notification type is required")
        
        # Create or update notification read record
        read_record = {
            "admin_id": current_user.get("id"),
            "type": notification_type,
            "read_at": datetime.now(timezone.utc)
        }
        
        if notification_id:
            read_record["item_id"] = notification_id
        
        # Store in read notifications collection
        await db.read_notifications.insert_one(read_record)
        
        logger.info(f"Notification marked as read: {notification_type} by {current_user.get('id')}")
        
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to mark as read: {str(e)}")

@api_router.post("/admin/notifications/dismiss-all")
async def dismiss_all_notifications(data: dict, current_user: dict = Depends(get_current_user)):
    """Dismiss all notifications of a specific type"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        notification_type = data.get("type")
        
        if not notification_type:
            raise HTTPException(status_code=400, detail="Notification type is required")
        
        # Record dismissal
        dismiss_record = {
            "admin_id": current_user.get("id"),
            "type": notification_type,
            "dismissed_at": datetime.now(timezone.utc)
        }
        
        await db.dismissed_notifications.insert_one(dismiss_record)
        
        logger.info(f"All {notification_type} notifications dismissed by {current_user.get('id')}")
        
        return {"message": f"All {notification_type} notifications dismissed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dismissing notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to dismiss: {str(e)}")


# ============= ADMIN PROFILE ENDPOINTS =============

@api_router.get("/admin/profile")
async def get_admin_profile(current_user: dict = Depends(get_current_user)):
    """Get admin profile"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        profile = await db.admin_profile.find_one({"id": "admin_profile"}, {"_id": 0, "password_hash": 0})
        
        if not profile:
            # Return default profile if not exists
            profile = {
                "id": "admin_profile",
                "mobile": None,
                "email": None
            }
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching admin profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@api_router.put("/admin/profile")
async def update_admin_profile(
    profile_update: AdminProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update admin profile (mobile and email only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        update_data = {}
        if profile_update.mobile is not None:
            update_data["mobile"] = profile_update.mobile
        if profile_update.email is not None:
            update_data["email"] = profile_update.email
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        result = await db.admin_profile.update_one(
            {"id": "admin_profile"},
            {"$set": update_data},
            upsert=True
        )
        
        return {"message": "Profile updated successfully", "updated_fields": list(update_data.keys())}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating admin profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@api_router.post("/admin/profile/send-otp")
async def send_otp_for_password_change(
    otp_request: SendOTPRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send OTP to admin email for password change"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Calculate expiry (10 minutes from now)
        expires_at = datetime.now(timezone.utc).timestamp() + (10 * 60)
        
        # Save OTP to database
        otp_data = {
            "email": otp_request.email,
            "otp": otp,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc)
        }
        
        # Delete any existing OTPs for this email
        await db.otp_verifications.delete_many({"email": otp_request.email})
        
        # Insert new OTP
        await db.otp_verifications.insert_one(otp_data)
        
        # Send OTP email using Gmail service
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            gmail_email = os.getenv("GMAIL_EMAIL")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD")
            
            if not gmail_email or not gmail_password:
                raise HTTPException(status_code=500, detail="Email service not configured")
            
            msg = MIMEMultipart()
            msg['From'] = gmail_email
            msg['To'] = otp_request.email
            msg['Subject'] = "Password Change OTP - Anantha Lakshmi Admin"
            
            body = f"""
            <html>
            <body>
                <h2>Password Change OTP</h2>
                <p>Your OTP for password change is: <strong style="font-size: 24px; color: #FF6B35;">{otp}</strong></p>
                <p>This OTP will expire in 10 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
                <br>
                <p>Thank you,<br>Anantha Lakshmi Team</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email via Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(gmail_email, gmail_password)
                server.send_message(msg)
            
            logger.info(f"OTP sent successfully to {otp_request.email}")
            
        except Exception as email_error:
            logger.error(f"Failed to send OTP email: {str(email_error)}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email")
        
        return {"message": f"OTP sent successfully to {otp_request.email}", "expires_in_minutes": 10}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@api_router.post("/admin/profile/verify-otp-change-password")
async def verify_otp_and_change_password(
    verify_request: VerifyOTPAndChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """Verify OTP and change admin password"""
    try:
        logger.info(f"Password change request received for email: {verify_request.email}")
        
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Find OTP record
        otp_record = await db.otp_verifications.find_one(
            {"email": verify_request.email, "otp": verify_request.otp},
            {"_id": 0}
        )
        
        if not otp_record:
            logger.warning(f"Invalid OTP attempt for email: {verify_request.email}")
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        # Check if OTP is expired
        expires_at = otp_record.get("expires_at")
        if isinstance(expires_at, datetime):
            # Ensure both datetimes have timezone info for comparison
            if expires_at.tzinfo is None:
                # If expires_at is naive, assume it's UTC
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            current_time = datetime.now(timezone.utc)
            
            if expires_at < current_time:
                # Delete expired OTP
                await db.otp_verifications.delete_one({"email": verify_request.email, "otp": verify_request.otp})
                raise HTTPException(status_code=400, detail="OTP has expired")
        
        # OTP is valid, change password
        # Update admin password in environment (this is for the current session)
        # In production, you'd want to update this in a secure database
        
        # For now, we'll update the ADMIN_PASSWORD environment variable
        # Note: This only persists in the .env file
        new_password_hash = get_password_hash(verify_request.new_password)
        
        # Update admin profile with new password hash
        await db.admin_profile.update_one(
            {"id": "admin_profile"},
            {"$set": {"password_hash": new_password_hash}},
            upsert=True
        )
        
        # Also update .env file for persistence
        try:
            env_path = ROOT_DIR / '.env'
            if env_path.exists():
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                with open(env_path, 'w') as f:
                    for line in lines:
                        if line.startswith('ADMIN_PASSWORD='):
                            f.write(f'ADMIN_PASSWORD="{verify_request.new_password}"\n')
                        else:
                            f.write(line)
                logger.info("Successfully updated .env file with new password")
        except Exception as env_error:
            # Log but don't fail if .env update fails
            logger.warning(f"Failed to update .env file: {str(env_error)}")
        
        # Delete used OTP
        await db.otp_verifications.delete_one({"email": verify_request.email, "otp": verify_request.otp})
        
        logger.info(f"Admin password changed successfully")
        
        return {"message": "Password changed successfully! Please login again with your new password."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

# Bug Report endpoint (Legacy - keep for backward compatibility)
@api_router.post("/report-issue")
async def report_issue(
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    issue_title: str = Form(...),
    description: str = Form(...),
    page: str = Form(None),
    screenshot: UploadFile = File(None)
):
    """Handle bug/issue reports from customers"""
    try:
        screenshot_path = None
        
        # Save screenshot if provided
        if screenshot:
            screenshot_filename = f"issue_{uuid.uuid4()}_{screenshot.filename}"
            screenshot_path = f"/app/frontend/public/uploads/{screenshot_filename}"
            
            with open(screenshot_path, "wb") as buffer:
                content = await screenshot.read()
                buffer.write(content)
            
            screenshot_path = f"/uploads/{screenshot_filename}"
        
        issue_report = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "phone": phone,
            "issue_title": issue_title,
            "description": description,
            "page": page,
            "screenshot": screenshot_path,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "open"
        }
        
        await db.issue_reports.insert_one(issue_report)
        
        return {"message": "Issue report submitted successfully", "report_id": issue_report["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit issue report: {str(e)}")

# ============= WHATSAPP NUMBERS MANAGEMENT =============

@api_router.get("/admin/whatsapp-numbers")
async def get_whatsapp_numbers(current_user: dict = Depends(get_current_user)):
    """Get all WhatsApp numbers (Admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        numbers = await db.whatsapp_numbers.find({}, {"_id": 0}).sort("created_at", 1).to_list(5)
        
        # Convert datetime to ISO string
        for num in numbers:
            if isinstance(num.get("created_at"), datetime):
                num["created_at"] = num["created_at"].isoformat()
        
        return numbers
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching WhatsApp numbers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch WhatsApp numbers: {str(e)}")

@api_router.post("/admin/whatsapp-numbers")
async def add_whatsapp_number(
    number_data: WhatsAppNumberCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a WhatsApp number (Admin only, max 5 numbers)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if already 5 numbers exist
        count = await db.whatsapp_numbers.count_documents({})
        if count >= 5:
            raise HTTPException(status_code=400, detail="Maximum 5 WhatsApp numbers allowed")
        
        # Check if number already exists
        existing = await db.whatsapp_numbers.find_one({"phone": number_data.phone})
        if existing:
            raise HTTPException(status_code=400, detail="This WhatsApp number already exists")
        
        # Create new number
        new_number = WhatsAppNumber(
            phone=number_data.phone,
            name=number_data.name
        )
        
        await db.whatsapp_numbers.insert_one(new_number.model_dump())
        
        return {"message": "WhatsApp number added successfully", "id": new_number.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding WhatsApp number: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add WhatsApp number: {str(e)}")

@api_router.put("/admin/whatsapp-numbers/{number_id}")
async def update_whatsapp_number(
    number_id: str,
    number_data: WhatsAppNumberCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update a WhatsApp number (Admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if number already exists with different id
        existing = await db.whatsapp_numbers.find_one({
            "phone": number_data.phone,
            "id": {"$ne": number_id}
        })
        if existing:
            raise HTTPException(status_code=400, detail="This WhatsApp number already exists")
        
        result = await db.whatsapp_numbers.update_one(
            {"id": number_id},
            {"$set": {"phone": number_data.phone, "name": number_data.name}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="WhatsApp number not found")
        
        return {"message": "WhatsApp number updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating WhatsApp number: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update WhatsApp number: {str(e)}")

@api_router.delete("/admin/whatsapp-numbers/{number_id}")
async def delete_whatsapp_number(
    number_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a WhatsApp number (Admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await db.whatsapp_numbers.delete_one({"id": number_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="WhatsApp number not found")
        
        return {"message": "WhatsApp number deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting WhatsApp number: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete WhatsApp number: {str(e)}")

# ============= PAYMENT SETTINGS =============

@api_router.get("/admin/payment-settings")
async def get_payment_settings(current_user: dict = Depends(get_current_user)):
    """Get payment settings (Admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        settings = await db.payment_settings.find_one({}, {"_id": 0})
        
        if not settings:
            # Return default settings
            return {"status": "enabled", "updated_at": datetime.now(timezone.utc).isoformat()}
        
        # Convert datetime to ISO string
        if isinstance(settings.get("updated_at"), datetime):
            settings["updated_at"] = settings["updated_at"].isoformat()
        
        return settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment settings: {str(e)}")

@api_router.get("/payment-settings")
async def get_public_payment_settings():
    """Get payment settings for public (no auth required)"""
    try:
        settings = await db.payment_settings.find_one({}, {"_id": 0})
        
        if not settings:
            # Return default settings
            return {"status": "enabled"}
        
        return {"status": settings.get("status", "enabled")}
    except Exception as e:
        logger.error(f"Error fetching payment settings: {str(e)}")
        # Return default on error
        return {"status": "enabled"}

@api_router.put("/admin/payment-settings")
async def update_payment_settings(
    status: str,
    current_user: dict = Depends(get_current_user)
):
    """Update payment settings (Admin only)"""
    try:
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Validate status
        valid_statuses = ["enabled", "disabled", "removed"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update or create settings
        settings = PaymentSettings(status=status)
        
        await db.payment_settings.update_one(
            {},
            {"$set": settings.model_dump()},
            upsert=True
        )
        
        logger.info(f"Payment settings updated to: {status}")
        
        return {"message": "Payment settings updated successfully", "status": status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payment settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update payment settings: {str(e)}")


# ============= CUSTOMER DATA BY PHONE NUMBER =============

@api_router.get("/customer-data/{phone}")
async def get_customer_data_by_phone(phone: str):
    """Get customer data by phone number (no auth required for convenience)"""
    try:
        # Clean phone number
        cleaned_phone = phone.replace("+91", "").replace(" ", "").replace("-", "")
        
        # Try to find customer data by phone
        customer = await db.customer_data.find_one(
            {"phone": {"$regex": f".*{cleaned_phone}.*"}}, 
            {"_id": 0}
        )
        
        if not customer:
            return None
        
        # Convert datetime to ISO string
        if isinstance(customer.get("last_updated"), datetime):
            customer["last_updated"] = customer["last_updated"].isoformat()
        
        return customer
    except Exception as e:
        logger.error(f"Error fetching customer data: {str(e)}")
        return None

@api_router.post("/customer-data")
async def save_customer_data(customer_data: CustomerData):
    """Save or update customer data by phone number"""
    try:
        # Update or create customer data
        await db.customer_data.update_one(
            {"phone": customer_data.phone},
            {"$set": customer_data.model_dump()},
            upsert=True
        )
        
        logger.info(f"Customer data saved for phone: {customer_data.phone}")
        
        return {"message": "Customer data saved successfully"}
    except Exception as e:
        logger.error(f"Error saving customer data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save customer data: {str(e)}")

# ============= WHATSAPP NUMBERS PUBLIC ENDPOINT =============

@api_router.get("/whatsapp-numbers")
async def get_public_whatsapp_numbers():
    """Get all WhatsApp numbers for public use (no auth required)"""
    try:
        numbers = await db.whatsapp_numbers.find({}, {"_id": 0, "phone": 1, "name": 1}).to_list(5)
        return numbers
    except Exception as e:
        logger.error(f"Error fetching public WhatsApp numbers: {str(e)}")
        return []

# Include router
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Anantha Lakshmi API Server", "status": "running"}
