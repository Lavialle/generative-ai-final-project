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
QDRANT_CLOUD_URL = os.getenv("QDRANT_CLOUD_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Vérifier que les clés API sont définies
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is missing. Please check your .env file.")
if not all([R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, BUCKET_NAME]):
    raise ValueError("R2 Storage configuration is incomplete. Please check your .env file.")
if not all([QDRANT_CLOUD_URL, QDRANT_API_KEY]):
    raise ValueError("Qdrant Cloud configuration is incomplete. Please check your .env file.")