"""Admin user management - Auto-create/update admin from .env"""
import os
import logging
from auth import get_password_hash

logger = logging.getLogger(__name__)

async def ensure_admin_exists_mongodb(db):
    """
    Ensure admin user exists in MongoDB with credentials from .env
    Creates or updates admin user on server startup
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@ananthalakshmi.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        # Check if admin exists
        admin_profile = await db.admin_profiles.find_one({"id": "admin_profile"})
        
        # Hash the password
        password_hash = get_password_hash(admin_password)
        
        if admin_profile:
            # Update existing admin if credentials changed
            if (admin_profile.get('email') != admin_email or 
                admin_profile.get('password_hash') != password_hash):
                
                await db.admin_profiles.update_one(
                    {"id": "admin_profile"},
                    {
                        "$set": {
                            "email": admin_email,
                            "password_hash": password_hash
                        }
                    }
                )
                logger.info(f"✅ Admin credentials updated from .env: {admin_email}")
            else:
                logger.info(f"✅ Admin user already exists: {admin_email}")
        else:
            # Create new admin
            await db.admin_profiles.insert_one({
                "id": "admin_profile",
                "email": admin_email,
                "password_hash": password_hash,
                "mobile": None
            })
            logger.info(f"✅ Admin user created from .env: {admin_email}")
            
    except Exception as e:
        logger.error(f"❌ Error ensuring admin exists: {e}")
        raise


async def ensure_admin_exists_postgresql(pool):
    """
    Ensure admin user exists in PostgreSQL with credentials from .env
    Creates or updates admin user on server startup
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@ananthalakshmi.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        # Hash the password
        password_hash = get_password_hash(admin_password)
        
        async with pool.acquire() as conn:
            # Check if admin exists
            admin_profile = await conn.fetchrow(
                "SELECT * FROM admin_profiles WHERE id = $1",
                "admin_profile"
            )
            
            if admin_profile:
                # Update existing admin if credentials changed
                if (admin_profile['email'] != admin_email or 
                    admin_profile['password_hash'] != password_hash):
                    
                    await conn.execute(
                        """
                        UPDATE admin_profiles 
                        SET email = $1, password_hash = $2 
                        WHERE id = $3
                        """,
                        admin_email, password_hash, "admin_profile"
                    )
                    logger.info(f"✅ Admin credentials updated from .env: {admin_email}")
                else:
                    logger.info(f"✅ Admin user already exists: {admin_email}")
            else:
                # Create new admin
                await conn.execute(
                    """
                    INSERT INTO admin_profiles (id, email, password_hash, mobile) 
                    VALUES ($1, $2, $3, $4)
                    """,
                    "admin_profile", admin_email, password_hash, None
                )
                logger.info(f"✅ Admin user created from .env: {admin_email}")
                
    except Exception as e:
        logger.error(f"❌ Error ensuring admin exists: {e}")
        raise
