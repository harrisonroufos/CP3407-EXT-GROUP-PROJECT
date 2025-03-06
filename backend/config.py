from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file automatically

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL is missing! Check your .env file.")
else:
    print(f"📌 Using DATABASE_URL: {DATABASE_URL}")
