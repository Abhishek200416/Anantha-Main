# Distance calculator using Haversine formula
import math
import requests
import os

# Guntur coordinates (fixed reference point)
GUNTUR_LAT = 16.3067
GUNTUR_LON = 80.4365

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r

def get_coordinates(city_name, state_name):
    """
    Get coordinates of a city using OpenStreetMap Nominatim API
    Returns (latitude, longitude) or None if not found
    """
    try:
        # Build search query
        query = f"{city_name}, {state_name}, India"
        
        # Call Nominatim API
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'AnanthaLakshmi-FoodDelivery/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
        
        return None
    except Exception as e:
        print(f"Error getting coordinates for {city_name}, {state_name}: {str(e)}")
        return None

def calculate_distance_from_guntur(city_name, state_name):
    """
    Calculate distance from Guntur to given city
    Returns distance in km or None if coordinates not found
    """
    coords = get_coordinates(city_name, state_name)
    if coords:
        lat, lon = coords
        distance = haversine_distance(GUNTUR_LAT, GUNTUR_LON, lat, lon)
        return round(distance, 2)
    return None

def get_delivery_charge_from_distance(distance_km):
    """
    Calculate delivery charge based on distance
    Tier-based pricing:
    - 0-50km: ₹49
    - 51-100km: ₹99
    - 101-200km: ₹149
    - 200+km: ₹199
    """
    if distance_km <= 50:
        return 49
    elif distance_km <= 100:
        return 99
    elif distance_km <= 200:
        return 149
    else:
        return 199

def calculate_delivery_charge_for_custom_city(city_name, state_name):
    """
    Calculate delivery charge for a custom city
    Returns (delivery_charge, distance_km, coordinates) or (199, None, None) if calculation fails
    """
    try:
        # Get coordinates
        coords = get_coordinates(city_name, state_name)
        if not coords:
            # Default to highest charge if we can't find the city
            return (199, None, None)
        
        lat, lon = coords
        
        # Calculate distance
        distance = haversine_distance(GUNTUR_LAT, GUNTUR_LON, lat, lon)
        distance = round(distance, 2)
        
        # Get delivery charge based on distance
        charge = get_delivery_charge_from_distance(distance)
        
        return (charge, distance, coords)
    except Exception as e:
        print(f"Error calculating delivery charge for {city_name}, {state_name}: {str(e)}")
        return (199, None, None)
