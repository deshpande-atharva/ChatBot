import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing connection to: {DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('//')[1].split(':')[1], '***')}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Successfully connected to MySQL!")
        
        # Test if database exists
        result = connection.execute(text("SELECT DATABASE()"))
        db_name = result.scalar()
        print(f"✅ Connected to database: {db_name}")
        
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    print("\nTroubleshooting tips:")
    print("1. Make sure MySQL is running")
    print("2. Check your password in the .env file")
    print("3. Ensure 'bindiq_chatbot' database exists")