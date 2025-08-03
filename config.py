# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables depuis .env

# Clés et variables de configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Exemple d'autres options (à personnaliser)
MODEL_NAME = "gpt-4.1-mini"
TEMPERATURE = 0.7
