# # Utilise une image de base Python officielle avec Python 3.11
# FROM python:3.11

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     libx11-xcb1 \
#     libxrender1 \
#     libxkbcommon-x11-0 \
#     qt5-default \
#     && rm -rf /var/lib/apt/lists/*


# # Définir le répertoire de travail dans le conteneur
# WORKDIR /app/backend

# # Copier les fichiers de dépendances
# COPY . .

# # Installer les dépendances
# RUN pip install --no-cache-dir -r requirements.txt 

# # Copier le reste du code de l'application


# # Exposer le port sur lequel Streamlit fonctionne
# EXPOSE 8000

# # Commande pour démarrer l'application Streamlit
# CMD ["uvicorn", "backend.app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Utiliser l'image python slim comme base
FROM python:3.11

# Mettre à jour les sources et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libx11-xcb1 \
    libxrender1 \
    libxkbcommon-x11-0 \
    qtbase5-dev \
    qtchooser \
    && rm -rf /var/lib/apt/lists/*

# Copier le code de l'application
WORKDIR /app
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app


# # Commande par défaut à exécuter pour lancer l'application
# CMD ["uvicorn", "app:app/backend", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ➤ On va dans le dossier backend pour lancer le app.py avec uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

