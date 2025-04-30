import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

# Récupérer la clé API depuis .env
API_KEY = os.getenv("TMDB_API_KEY")
if not API_KEY:
    raise ValueError("Clé API manquante ! Vérifie ton fichier .env")

# Requête vers l’API de TMDB
url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
response = requests.get(url, headers=headers)
genres_data = response.json()["genres"]

# Création du dictionnaire id → nom
genre_map = {genre["id"]: genre["name"] for genre in genres_data}

df = pd.read_csv("data/movies.csv")

def convert_genres(genre_ids_str):
    # Nettoyer et convertir en liste d'int
    if pd.isna(genre_ids_str):
        return "" 

    genre_ids = [int(g.strip()) for g in str(genre_ids_str).split(",")]
    # Mapper chaque ID au nom via genre_map
    genre_names = [genre_map.get(gid, f"Unknown({gid})") for gid in genre_ids]
    return ", ".join(genre_names)

# Appliquer à la colonne
df["genres"] = df["genres"].apply(convert_genres)


df.to_csv("data/movies.csv", index=False)
