import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Supabase configuration
supabase_url = os.getenv("SUPABASE_PROJECT_URL", "")
supabase_key = os.getenv("SUPABASE_ANON_PUBLIC_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

# Security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS = eval(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:5173"]'))
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Test mode configuration (for development only)
ENABLE_TEST_MODE = os.getenv("ENABLE_TEST_MODE", "false").lower() == "true"
TEST_USER_ID = os.getenv("TEST_USER_ID", "")
TEST_ACCESS_TOKEN = os.getenv("TEST_ACCESS_TOKEN", "")

# Validate required configuration
if not supabase_url or not supabase_key:
    raise ValueError("Missing required Supabase configuration. Please check your .env file.")

if ENVIRONMENT == "production" and ENABLE_TEST_MODE:
    raise ValueError("Test mode cannot be enabled in production environment.")
