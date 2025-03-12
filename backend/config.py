from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "False").lower() == "true"

if USE_LOCAL_DB:
    DB_DIR = "database_files"  # relative directory (in the project root)
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    DATABASE_PATH = os.path.join(DB_DIR, "MyClean_Database.db")
    DATABASE_URL = DATABASE_PATH  # Use relative path
else:
    DATABASE_URL = os.getenv("DATABASE_URL")  # Use PostgreSQL connection string

if not DATABASE_URL:
    print("❌ DATABASE_URL is missing! Check your .env file.")
else:
    print(f"📌 Using {'SQLite' if USE_LOCAL_DB else 'PostgreSQL'} database: {DATABASE_URL}")
