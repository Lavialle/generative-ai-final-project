import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
if os.path.exists(".env"):
    load_dotenv()
    print("Environment variables loaded from .env file.")

# Récupérer les clés API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Vérifier que les clés API sont définies
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is missing. Please check your .env file.")
if not SERP_API_KEY:
    raise ValueError("SerpAPI Key is missing. Please check your .env file.")