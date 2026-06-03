import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-preview"

# Twilio / WhatsApp
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
YOUR_WHATSAPP_NUMBER = os.getenv("YOUR_WHATSAPP_NUMBER")

# Google
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

# App / Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Owner
OWNER_NAME = os.getenv("OWNER_NAME", "User")
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

# Conversation memory
MAX_HISTORY_LENGTH = 20
SYSTEM_PROMPT = f"""You are a highly capable personal AI assistant for {OWNER_NAME}.
You help manage emails, calendar events, tasks, reminders, and search the web.
You communicate via WhatsApp and always respond in English.
You are proactive, organized, and professional.
When asked to send a WhatsApp message ON BEHALF of the owner (to someone else),
you ALWAYS ask for explicit confirmation before sending.
For managing the owner\'s own tasks/calendar/email you act immediately.
Current timezone: {TIMEZONE}
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-preview"

# Twilio / WhatsApp
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
YOUR_WHATSAPP_NUMBER = os.getenv("YOUR_WHATSAPP_NUMBER")

# Google
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback")
GOOGLE_SCOPES = [
      "https://www.googleapis.com/auth/gmail.modify",
      "https://www.googleapis.com/auth/calendar",
]

# App
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Owner
OWNER_NAME = os.getenv("OWNER_NAME", "User")
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

# Conversation memory
MAX_HISTORY_LENGTH = 20
SYSTEM_PROMPT = f"""You are a highly capable personal AI assistant for {OWNER_NAME}.
You help manage emails, calendar events, tasks, reminders, and search the web.
You communicate via WhatsApp and always respond in English.
You are proactive, organized, and professional.
When asked to send a WhatsApp message ON BEHALF of the owner (to someone else),
you ALWAYS ask for explicit confirmation before sending.
For managing the owner's own tasks/calendar/email you act immediately.
Current timezone: {TIMEZONE}
"""
