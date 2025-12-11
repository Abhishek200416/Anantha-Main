import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from cities_data import ANDHRA_PRADESH_CITIES, TELANGANA_CITIES, DEFAULT_DELIVERY_CHARGES, DEFAULT_OTHER_CITY_CHARGE
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'anantha_lakshmi_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
print(f"📦 Using database: {DB_NAME}")

async def seed_cities():
    """Seed database with all cities from Andhra Pradesh and Telangana"""
    
    # Clear existing locations
    await db.locations.delete_many({})
    print("🗑️  Cleared existing cities")
    
    cities_to_add = []
    
    # Add Andhra Pradesh cities
    for city in ANDHRA_PRADESH_CITIES:
        delivery_charge = DEFAULT_DELIVERY_CHARGES.get(city, DEFAULT_OTHER_CITY_CHARGE)
        city_data = {
            "name": city,
            "state": "Andhra Pradesh",
            "charge": delivery_charge,
            "free_delivery_threshold": None,
            "enabled": True
        }
        cities_to_add.append(city_data)
    
    # Add Telangana cities
    for city in TELANGANA_CITIES:
        delivery_charge = DEFAULT_DELIVERY_CHARGES.get(city, DEFAULT_OTHER_CITY_CHARGE)
        city_data = {
            "name": city,
            "state": "Telangana",
            "charge": delivery_charge,
            "free_delivery_threshold": None,
            "enabled": True
        }
        cities_to_add.append(city_data)
    
    # Insert all cities
    if cities_to_add:
        await db.locations.insert_many(cities_to_add)
        print(f"✅ Successfully added {len(cities_to_add)} cities to database")
        
        # Count by state
        ap_count = len([c for c in cities_to_add if c['state'] == 'Andhra Pradesh'])
        ts_count = len([c for c in cities_to_add if c['state'] == 'Telangana'])
        
        print(f"\n📊 City Summary:")
        print(f"   Andhra Pradesh: {ap_count} cities")
        print(f"   Telangana: {ts_count} cities")
        print(f"   Total: {len(cities_to_add)} cities")
        
        # Show some examples
        print(f"\n📍 Sample cities added:")
        for city in cities_to_add[:10]:
            print(f"   - {city['name']} ({city['state']}) - ₹{city['charge']}")
        
        print(f"\n🎉 Database seeding completed successfully!")
    else:
        print("❌ No cities to add")

if __name__ == "__main__":
    asyncio.run(seed_cities())
