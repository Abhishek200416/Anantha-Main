from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid

# ============= PRODUCT MODELS =============

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
