# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables depuis .env

# Clés et variables de configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Clés et variables de configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Exemple d'autres options (à personnaliser)
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0.7

GROQ_API_BASE = "https://api.groq.com/openai/v1"  # Spécifique à Groq
GROQ_MODEL = "llama3-70b-8192"


MONGO_URI = os.getenv("MONGO_URI")