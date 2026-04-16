import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    uri = os.getenv("DATABASE_URL")

    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
    # DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    # WhatsApp
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v18.0")
    WHATSAPP_BASE_URL = f"https://graph.facebook.com/{os.getenv('WHATSAPP_API_VERSION', 'v18.0')}/{os.getenv('PHONE_NUMBER_ID')}/messages"

    # Webhook
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

    # App
    APP_URL = os.getenv("APP_URL", "http://localhost:5000")

    # Matching Settings
    INITIAL_DONOR_BATCH = 5          # How many donors to alert first
    EXPAND_WAIT_MINUTES = 10         # Minutes before expanding search radius
    INITIAL_RADIUS_KM = 10           # First search radius in KM
    EXPAND_RADIUS_KM = 25            # Expanded radius in KM
    MAX_RADIUS_KM = 50               # Maximum search radius in KM
    DONATION_GAP_DAYS = 90           # Minimum days between donations
    DONOR_PING_INTERVAL_DAYS = 30    # How often to ping donors
    DONOR_INACTIVE_AFTER_HOURS = 48  # Mark inactive if no ping reply