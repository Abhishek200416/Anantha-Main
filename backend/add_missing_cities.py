import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from cities_data import ALL_CITIES, DEFAULT_DELIVERY_CHARGES, DEFAULT_OTHER_CITY_CHARGE
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.food_delivery

# State mapping for cities
STATE_MAPPING = {
    # Andhra Pradesh cities
    "Visakhapatnam": "Andhra Pradesh", "Vijayawada": "Andhra Pradesh", "Guntur": "Andhra Pradesh",
    "Nellore": "Andhra Pradesh", "Tirupati": "Andhra Pradesh", "Kakinada": "Andhra Pradesh",
    "Rajahmundry": "Andhra Pradesh", "Anantapur": "Andhra Pradesh", "Kurnool": "Andhra Pradesh",
    "Kadapa": "Andhra Pradesh", "Vizianagaram": "Andhra Pradesh", "Eluru": "Andhra Pradesh",
    "Ongole": "Andhra Pradesh", "Nandyal": "Andhra Pradesh", "Srikakulam": "Andhra Pradesh",
    "Chittoor": "Andhra Pradesh", "Prakasam": "Andhra Pradesh", "Krishna": "Andhra Pradesh",
    "Machilipatnam": "Andhra Pradesh", "Bhimavaram": "Andhra Pradesh", "Hindupur": "Andhra Pradesh",
    "Tenali": "Andhra Pradesh", "Proddatur": "Andhra Pradesh", "Adoni": "Andhra Pradesh",
    "Narasaraopet": "Andhra Pradesh", "Kavali": "Andhra Pradesh", "Gudivada": "Andhra Pradesh",
    "Chirala": "Andhra Pradesh", "Madanapalle": "Andhra Pradesh", "Chilakaluripet": "Andhra Pradesh",
    "Dharmavaram": "Andhra Pradesh", "Tadepalligudem": "Andhra Pradesh", "Palakollu": "Andhra Pradesh",
    "Puttur": "Andhra Pradesh", "Bapatla": "Andhra Pradesh", "Sattenapalle": "Andhra Pradesh",
    "Markapur": "Andhra Pradesh", "Vinukonda": "Andhra Pradesh", "Guntakal": "Andhra Pradesh",
    "Srikalahasti": "Andhra Pradesh", "Repalle": "Andhra Pradesh", "Amalapuram": "Andhra Pradesh",
    "Bobbili": "Andhra Pradesh", "Samalkot": "Andhra Pradesh", "Tanuku": "Andhra Pradesh",
    "Narasapuram": "Andhra Pradesh", "Mangalagiri": "Andhra Pradesh", "Ponnur": "Andhra Pradesh",
    "Nambur": "Andhra Pradesh", "Pedakakani": "Andhra Pradesh", "Kollipara": "Andhra Pradesh",
    "Duggirala": "Andhra Pradesh", "Gurazala": "Andhra Pradesh", "Macherla": "Andhra Pradesh",
    "Amaravathi": "Andhra Pradesh", "Prathipadu": "Andhra Pradesh", "Phirangipuram": "Andhra Pradesh",
    "Medikonduru": "Andhra Pradesh", "Rentachintala": "Andhra Pradesh", "Piduguralla": "Andhra Pradesh",
    
    # Telangana cities
    "Hyderabad": "Telangana", "Secunderabad": "Telangana", "Warangal": "Telangana",
    "Nizamabad": "Telangana", "Karimnagar": "Telangana", "Khammam": "Telangana",
    "Ramagundam": "Telangana", "Mahbubnagar": "Telangana", "Nalgonda": "Telangana",
    "Adilabad": "Telangana", "Suryapet": "Telangana", "Miryalaguda": "Telangana",
    "Jagtial": "Telangana", "Mancherial": "Telangana", "Nirmal": "Telangana",
    "Kamareddy": "Telangana", "Siddipet": "Telangana", "Wanaparthy": "Telangana",
}

async def add_missing_cities():
    """Add all cities from cities_data.py to the database if they don't exist"""
    
    # Get existing cities
    existing_cities = await db.locations.find({}, {"name": 1, "_id": 0}).to_list(1000)
    existing_city_names = {city["name"] for city in existing_cities}
    
    print(f"Found {len(existing_city_names)} existing cities in database")
    
    # Find missing cities
    missing_cities = [city for city in ALL_CITIES if city not in existing_city_names]
    
    if not missing_cities:
        print("No missing cities. Database is up to date!")
        return
    
    print(f"\nAdding {len(missing_cities)} missing cities:")
    
    # Add missing cities
    for city_name in missing_cities:
        # Determine delivery charge
        delivery_charge = DEFAULT_DELIVERY_CHARGES.get(city_name, DEFAULT_OTHER_CITY_CHARGE)
        
        # Determine state - default to Andhra Pradesh if not in mapping
        state = STATE_MAPPING.get(city_name, "Andhra Pradesh")
        
        city_doc = {
            "name": city_name,
            "state": state,
            "charge": delivery_charge,
            "enabled": True,
            "free_delivery_threshold": 1000 if state == "Andhra Pradesh" else 1500
        }
        
        try:
            await db.locations.insert_one(city_doc)
            print(f"✓ Added: {city_name}, {state} (₹{delivery_charge})")
        except Exception as e:
            print(f"✗ Error adding {city_name}: {e}")
    
    # Get final count
    final_count = await db.locations.count_documents({})
    print(f"\n✅ Database now has {final_count} cities total")
    
    # Check for duplicates
    pipeline = [
        {"$group": {"_id": "$name", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = await db.locations.aggregate(pipeline).to_list(100)
    
    if duplicates:
        print(f"\n⚠️ Found {len(duplicates)} duplicate city names:")
        for dup in duplicates:
            print(f"  - {dup['_id']} appears {dup['count']} times")
            # Remove duplicates, keep only one
            cities_to_remove = await db.locations.find({"name": dup['_id']}).to_list(100)
            # Keep the first one, delete the rest
            for i, city in enumerate(cities_to_remove):
                if i > 0:  # Skip the first one
                    await db.locations.delete_one({"_id": city["_id"]})
                    print(f"    Removed duplicate entry for {dup['_id']}")
        
        # Recheck count after cleanup
        final_count = await db.locations.count_documents({})
        print(f"\n✅ After cleanup: Database has {final_count} unique cities")
    else:
        print("\n✅ No duplicate cities found!")

if __name__ == "__main__":
    asyncio.run(add_missing_cities())
