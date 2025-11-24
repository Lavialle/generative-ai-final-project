# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier uniquement requirements.txt d'abord pour profiter du cache Docker
COPY requirements.txt .

# Installer les dépendances (cette couche sera mise en cache si requirements.txt ne change pas)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --use-feature=fast-deps -r requirements.txt

# Copier le reste des fichiers de l'application
COPY . /app

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande pour lancer l'application Streamlit
CMD ["streamlit", "run", "app_chatbot.py", "--server.address", "0.0.0.0"]