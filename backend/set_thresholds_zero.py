"""
Script to set all free_delivery_threshold values to 0
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def set_all_thresholds_to_zero():
    """Set all city free_delivery_threshold to 0"""
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client.food_delivery
        
        # Update all locations to have free_delivery_threshold = 0
        result = await db.locations.update_many(
            {},  # Match all documents
            {"$set": {"free_delivery_threshold": 0}}
        )
        
        print(f"✅ Updated {result.modified_count} locations")
        print("All free_delivery_threshold values set to 0")
        
        # Verify the update
        all_locations = await db.locations.find({}, {"_id": 0, "name": 1, "free_delivery_threshold": 1}).to_list(1000)
        print(f"\nVerification: Found {len(all_locations)} locations")
        
        # Show first 5 as sample
        for loc in all_locations[:5]:
            print(f"  - {loc.get('name')}: threshold = {loc.get('free_delivery_threshold', 'NOT SET')}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(set_all_thresholds_to_zero())
