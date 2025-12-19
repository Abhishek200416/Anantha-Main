"""PostgreSQL Database Connection Manager"""
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional
import asyncpg
from asyncpg import Pool

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Global connection pool
pool: Optional[Pool] = None

async def init_db_pool():
    """Initialize PostgreSQL connection pool"""
    global pool
    
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_user = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password = os.getenv('POSTGRES_PASSWORD', '')
    postgres_db = os.getenv('POSTGRES_DB', 'anantha_lakshmi_db')
    
    database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    pool = await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=10,
        command_timeout=60
    )
    return pool

async def get_db_pool() -> Pool:
    """Get PostgreSQL connection pool"""
    global pool
    if pool is None:
        pool = await init_db_pool()
    return pool

async def close_db_pool():
    """Close PostgreSQL connection pool"""
    global pool
    if pool:
        await pool.close()
        pool = None

async def create_tables():
    """Create all necessary tables for PostgreSQL"""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                password_hash TEXT,
                auth_provider VARCHAR(50) DEFAULT 'email',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                name_telugu TEXT,
                category VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                description_telugu TEXT,
                image TEXT NOT NULL,
                prices JSONB NOT NULL,
                is_best_seller BOOLEAN DEFAULT FALSE,
                is_new BOOLEAN DEFAULT FALSE,
                tag VARCHAR(100) DEFAULT 'Traditional',
                discount_percentage FLOAT,
                discount_expiry_date VARCHAR(50),
                inventory_count INTEGER,
                out_of_stock BOOLEAN DEFAULT FALSE,
                available_cities TEXT[]
            )
        ''')
        
        # Orders table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(255) PRIMARY KEY,
                order_id VARCHAR(100) UNIQUE NOT NULL,
                tracking_code VARCHAR(50) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                customer_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                whatsapp_number VARCHAR(50),
                address TEXT NOT NULL,
                door_no VARCHAR(100),
                building VARCHAR(255),
                street VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(20),
                location VARCHAR(255) NOT NULL,
                items JSONB NOT NULL,
                subtotal FLOAT NOT NULL,
                delivery_charge FLOAT NOT NULL,
                total FLOAT NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                payment_sub_method VARCHAR(50),
                payment_status VARCHAR(50) DEFAULT 'pending',
                is_custom_location BOOLEAN DEFAULT FALSE,
                custom_city VARCHAR(255),
                custom_state VARCHAR(100),
                distance_from_guntur FLOAT,
                custom_city_request BOOLEAN DEFAULT FALSE,
                order_status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estimated_delivery VARCHAR(100),
                admin_notes TEXT,
                delivery_days INTEGER,
                cancelled BOOLEAN DEFAULT FALSE,
                cancelled_at TIMESTAMP,
                cancel_reason TEXT,
                cancellation_fee FLOAT DEFAULT 0.0
            )
        ''')
        
        # Locations table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                charge FLOAT NOT NULL,
                free_delivery_threshold FLOAT,
                state VARCHAR(100),
                enabled BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # States table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS states (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Admin profiles table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS admin_profiles (
                id VARCHAR(255) PRIMARY KEY,
                mobile VARCHAR(50),
                email VARCHAR(255),
                password_hash TEXT
            )
        ''')
        
        # Payment settings table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS payment_settings (
                id SERIAL PRIMARY KEY,
                status VARCHAR(50) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Razorpay settings table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS razorpay_settings (
                id SERIAL PRIMARY KEY,
                key_id VARCHAR(255) NOT NULL,
                key_secret VARCHAR(255) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # WhatsApp numbers table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_numbers (
                id VARCHAR(255) PRIMARY KEY,
                phone VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bug reports table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS bug_reports (
                id VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                mobile VARCHAR(50) NOT NULL,
                issue_description TEXT NOT NULL,
                photo_url TEXT,
                status VARCHAR(50) DEFAULT 'New',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Customer data table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS customer_data (
                phone VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                whatsapp VARCHAR(50),
                door_no VARCHAR(100),
                building VARCHAR(255),
                street VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(20),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ PostgreSQL tables created successfully")
