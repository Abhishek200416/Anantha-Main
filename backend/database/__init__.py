"""Database Package - Connection managers and models"""

# MongoDB connection (default)
try:
    from .connection_mongodb import get_database, get_client
    DATABASE_TYPE = "mongodb"
except Exception as e:
    print(f"MongoDB connection not available: {e}")
    DATABASE_TYPE = None

# PostgreSQL connection (optional)
try:
    from .connection_postgresql import (
        init_db_pool,
        get_db_pool,
        close_db_pool,
        create_tables
    )
    if DATABASE_TYPE is None:
        DATABASE_TYPE = "postgresql"
except Exception as e:
    print(f"PostgreSQL connection not available: {e}")

__all__ = [
    "DATABASE_TYPE",
    # MongoDB
    "get_database",
    "get_client",
    # PostgreSQL
    "init_db_pool",
    "get_db_pool",
    "close_db_pool",
    "create_tables"
]
