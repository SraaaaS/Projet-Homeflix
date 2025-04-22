# Utilise une image de base Python officielle avec Python 3.11
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libx11-xcb1 \
    libxrender1 \
    libxkbcommon-x11-0 \
    qt5-default \
    && rm -rf /var/lib/apt/lists/*


# Définir le répertoire de travail dans le conteneur
WORKDIR /app/backend

# Copier les fichiers de dépendances
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt 

# Copier le reste du code de l'application


# Exposer le port sur lequel Streamlit fonctionne
EXPOSE 8000

# Commande pour démarrer l'application Streamlit
CMD ["uvicorn", "backend.app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
