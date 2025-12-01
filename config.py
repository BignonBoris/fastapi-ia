# config.py
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()  # Charge les variables depuis .env

# Clés et variables de configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Clés et variables de configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Exemple d'autres options (à personnaliser)
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0.7

GROQ_API_BASE = "https://api.groq.com/openai/v1"  # Spécifique à Groq
# GROQ_MODEL = "llama3-70b-8192"
GROQ_MODEL = "llama-3.3-70b-versatile"
# GROQ_MODEL = "llama-3.1-8b-instant"
# GROQ_MODEL = "gemma2-9b-it"
# GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

MONGO_URI = os.getenv("MONGO_URI")

DB = AsyncIOMotorClient(MONGO_URI).sample_mflix  # Nom de ta base
API_URL = os.getenv("API_URL")