import os
import instaloader
from dotenv import load_dotenv

# Load .env file
load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

if not IG_USERNAME or not IG_PASSWORD:
    raise ValueError("Instagram credentials not found in .env")

L = instaloader.Instaloader()

print("🔐 Logging into Instagram...")
L.login(IG_USERNAME, IG_PASSWORD)

# Save session to avoid logging in again
L.save_session_to_file()

print("✅ Login successful, session saved.")
