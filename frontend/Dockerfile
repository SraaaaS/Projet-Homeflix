# Utilise une image de base Python officielle avec Python 3.9
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    linux-libc-dev \
    && rm -rf /var/lib/apt/lists/*


# Définir le répertoire de travail dans le conteneur
WORKDIR /app/frontend

# Copier les fichiers de dépendances
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application

# Exposer le port sur lequel FastAPI fonctionne
EXPOSE 8501

# Commande pour démarrer l'application FastAPI
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.adress=0.0.0.0"]

