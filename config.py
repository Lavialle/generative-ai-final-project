import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
if os.path.exists(".env"):
    load_dotenv()
    print("Environment variables loaded from .env file.")

# Récupérer les clés API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Vérifier que les clés API sont définies
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is missing. Please check your .env file.")