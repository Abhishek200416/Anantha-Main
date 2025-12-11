import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['anantha_lakshmi_db']

async def seed_states():
    """Seed database with only Andhra Pradesh and Telangana states"""
    
    # Clear existing states
    await db.states.delete_many({})
    print("🗑️  Cleared existing states")
    
    # Only add Andhra Pradesh and Telangana
    states_to_add = [
        {
            "name": "Andhra Pradesh",
            "enabled": True
        },
        {
            "name": "Telangana",
            "enabled": True
        }
    ]
    
    # Insert states
    await db.states.insert_many(states_to_add)
    print(f"✅ Successfully added {len(states_to_add)} states to database")
    
    print(f"\n📍 States added:")
    for state in states_to_add:
        print(f"   - {state['name']} (enabled: {state['enabled']})")
    
    print(f"\n🎉 Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_states())
