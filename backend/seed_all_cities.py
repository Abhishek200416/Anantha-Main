#!/usr/bin/env python3
"""
Seed all cities from cities_data.py into MongoDB database
This script adds all 419 cities from Andhra Pradesh and Telangana
"""
import os
import sys
from pymongo import MongoClient
from cities_data import ANDHRA_PRADESH_CITIES, TELANGANA_CITIES, DEFAULT_DELIVERY_CHARGES

def seed_all_cities():
    """Seed all cities from cities_data.py into database"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url)
    db = client['food_delivery']
    locations_collection = db.locations
    
    print("=" * 60)
    print("SEEDING ALL CITIES TO DATABASE")
    print("=" * 60)
    
    # Clear existing cities
    delete_result = locations_collection.delete_many({})
    print(f"\n✓ Cleared {delete_result.deleted_count} existing cities")
    
    cities_added = 0
    
    # Add Andhra Pradesh cities
    print(f"\n📍 Adding Andhra Pradesh cities...")
    for city in ANDHRA_PRADESH_CITIES:
        # Get delivery charge from default map or use 49 as default for AP
        charge = DEFAULT_DELIVERY_CHARGES.get(city, 49)
        
        city_doc = {
            "name": city,
            "state": "Andhra Pradesh",
            "charge": charge,
            "free_delivery_threshold": None,  # Can be set by admin later
            "enabled": True
        }
        
        locations_collection.insert_one(city_doc)
        cities_added += 1
    
    print(f"✓ Added {len(ANDHRA_PRADESH_CITIES)} Andhra Pradesh cities")
    
    # Add Telangana cities
    print(f"\n📍 Adding Telangana cities...")
    for city in TELANGANA_CITIES:
        # Get delivery charge from default map or use 99 as default for Telangana
        charge = DEFAULT_DELIVERY_CHARGES.get(city, 99)
        
        city_doc = {
            "name": city,
            "state": "Telangana",
            "charge": charge,
            "free_delivery_threshold": None,  # Can be set by admin later
            "enabled": True
        }
        
        locations_collection.insert_one(city_doc)
        cities_added += 1
    
    print(f"✓ Added {len(TELANGANA_CITIES)} Telangana cities")
    
    # Verify
    total_count = locations_collection.count_documents({})
    ap_count = locations_collection.count_documents({"state": "Andhra Pradesh"})
    tg_count = locations_collection.count_documents({"state": "Telangana"})
    
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE ✓")
    print("=" * 60)
    print(f"\nTotal cities in database: {total_count}")
    print(f"  • Andhra Pradesh: {ap_count} cities")
    print(f"  • Telangana: {tg_count} cities")
    
    # Show sample cities
    print("\nSample cities from database:")
    sample_cities = list(locations_collection.find({}, {"name": 1, "state": 1, "charge": 1, "_id": 0}).limit(10))
    for city in sample_cities:
        print(f"  • {city['name']}, {city['state']} - ₹{city['charge']}")
    
    print("\n✓ All cities are now available in:")
    print("  1. Admin panel - Cities & States tab")
    print("  2. Checkout page - City dropdown")
    print("\n" + "=" * 60)
    
    client.close()

if __name__ == "__main__":
    try:
        seed_all_cities()
    except Exception as e:
        print(f"\n❌ Error seeding cities: {str(e)}")
        sys.exit(1)
