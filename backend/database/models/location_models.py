from pydantic import BaseModel
from typing import Optional

# ============= LOCATION MODELS =============

class Location(BaseModel):
    name: str
    charge: float
    free_delivery_threshold: Optional[float] = None  # City-specific free delivery threshold
    state: Optional[str] = None

class State(BaseModel):
    name: str
    enabled: bool = True
