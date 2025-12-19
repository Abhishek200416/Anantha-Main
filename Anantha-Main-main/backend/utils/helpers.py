"""Helper utility functions"""
import random
import string
from datetime import datetime
from typing import Optional

def generate_order_id() -> str:
    """Generate unique order ID"""
    return f"AL{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

def generate_tracking_code() -> str:
    """Generate unique tracking code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance between two points on Earth (in kilometers)
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers
    R = 6371.0
    
    distance = R * c
    return distance
