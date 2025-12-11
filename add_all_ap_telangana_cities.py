#!/usr/bin/env python3
"""
Script to add ALL cities from Andhra Pradesh and Telangana to the database
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from cities_data import ANDHRA_PRADESH_CITIES, TELANGANA_CITIES, DEFAULT_DELIVERY_CHARGES, DEFAULT_OTHER_CITY_CHARGE

# Load environment variables
load_dotenv(Path(__file__).parent / 'backend' / '.env')

async def add_all_cities():
    """Add all AP and Telangana cities to database"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'anantha_lakshmi_db')
    
    print(f"Connecting to MongoDB: {mongo_url}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Count existing cities
    existing_count = await db.locations.count_documents({})
    print(f"\n📊 Existing cities in database: {existing_count}")
    
    # Prepare cities data
    cities_to_add = []
    ap_count = len(ANDHRA_PRADESH_CITIES)
    ts_count = len(TELANGANA_CITIES)
    total_cities = ap_count + ts_count
    
    print(f"\n🏙️  Total cities to process:")
    print(f"   - Andhra Pradesh: {ap_count} cities")
    print(f"   - Telangana: {ts_count} cities")
    print(f"   - TOTAL: {total_cities} cities")
    
    # Process Andhra Pradesh cities
    print(f"\n🔄 Processing Andhra Pradesh cities...")
    for city in ANDHRA_PRADESH_CITIES:
        # Check if city already exists
        existing = await db.locations.find_one({"name": city, "state": "Andhra Pradesh"})
        if existing:
            print(f"   ⏭️  Skipping {city} (already exists)")
            continue
        
        # Get delivery charge
        charge = DEFAULT_DELIVERY_CHARGES.get(city, DEFAULT_OTHER_CITY_CHARGE)
        
        city_data = {
            "name": city,
            "state": "Andhra Pradesh",
            "charge": charge,
            "free_delivery_threshold": 1000,  # Default threshold
            "enabled": True,
            "created_at": datetime.now(timezone.utc)
        }
        cities_to_add.append(city_data)
    
    # Process Telangana cities
    print(f"\n🔄 Processing Telangana cities...")
    for city in TELANGANA_CITIES:
        # Check if city already exists
        existing = await db.locations.find_one({"name": city, "state": "Telangana"})
        if existing:
            print(f"   ⏭️  Skipping {city} (already exists)")
            continue
        
        # Get delivery charge
        charge = DEFAULT_DELIVERY_CHARGES.get(city, DEFAULT_OTHER_CITY_CHARGE)
        
        city_data = {
            "name": city,
            "state": "Telangana",
            "charge": charge,
            "free_delivery_threshold": 1500 if city in ["Hyderabad", "Secunderabad"] else 1000,
            "enabled": True,
            "created_at": datetime.now(timezone.utc)
        }
        cities_to_add.append(city_data)
    
    # Add cities to database in batches
    if cities_to_add:
        print(f"\n✅ Adding {len(cities_to_add)} new cities to database...")
        await db.locations.insert_many(cities_to_add)
        print(f"✅ Successfully added {len(cities_to_add)} cities!")
    else:
        print(f"\n✅ All cities already exist in database!")
    
    # Final count
    final_count = await db.locations.count_documents({})
    print(f"\n📊 Final cities count in database: {final_count}")
    
    # Show breakdown by state
    ap_db_count = await db.locations.count_documents({"state": "Andhra Pradesh"})
    ts_db_count = await db.locations.count_documents({"state": "Telangana"})
    print(f"\n🏙️  Breakdown by state:")
    print(f"   - Andhra Pradesh: {ap_db_count} cities")
    print(f"   - Telangana: {ts_db_count} cities")
    print(f"   - TOTAL: {final_count} cities")
    
    # Close connection
    client.close()
    print(f"\n🎉 Done! All cities from AP & Telangana are now in the database!")

if __name__ == "__main__":
    asyncio.run(add_all_cities())
