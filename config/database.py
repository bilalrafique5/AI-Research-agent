# config/database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_research_agent")

def get_mongodb_client():
    """Get MongoDB client"""
    client = MongoClient(MONGODB_URL)
    return client

def get_database():
    """Get database instance"""
    client = get_mongodb_client()
    db = client[DATABASE_NAME]
    return db

def init_database():
    """Initialize database and create indexes"""
    db = get_database()
    
    # Create users collection with indexes
    if "users" not in db.list_collection_names():
        db.create_collection("users")
    
    # Create indexes
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    
    return db

# Initialize on import
db = init_database()
