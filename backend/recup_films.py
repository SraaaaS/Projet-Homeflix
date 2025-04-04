import requests
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/movie/popular"
# Chemin du dossier data
DATA_DIR = "data"
MOVIES_CSV = os.path.join(DATA_DIR, "movies.csv")
NUM_PAGES = 25  # Nombre de pages à récupérer

# Vérifier si le dossier existe, sinon le créer
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
else:
    print("Le dossier 'data' existe deja")


def fetch_movies():
    """Récupère les 10premieres pages des films populaires depuis TMDB et les enregistre dans movies.csv"""
    all_movies = [] #liste stockant tous les films
    
    for page in range(1, NUM_PAGES +1):
        url = f"{BASE_URL}?api_key={API_KEY}&language=fr-FR&page={page}"
        response = requests.get(url)
    
        if response.status_code != 200:
            print(":x: Erreur lors de la récupération des films depuis TMDB")
            continue #passer a la page suivante

        data = response.json()
        movies = data.get("results", []) #Si "results" existe, .get("results") renvoie la liste de films sinon renvoie une liste vide ([]) au lieu de provoquer une erreur

        if not movies:
            print("Aucune donnée récupérée pour la page {page}")
            continue

    # Extraction des informations importantes
        for movie in movies:
            all_movies.append( {
            "id": movie["id"],
            "title": movie["title"],
            "genres": ", ".join([str(genre) for genre in movie.get("genre_ids", [])]),
            "release_date": movie["release_date"],
            "vote_average": movie["vote_average"],
        })
            
        print(f"La page {page} recuperee contient {len(movies)} films")
        

    # Sauvegarde en CSV
    df = pd.DataFrame(all_movies)
    df.to_csv(f"./{DATA_DIR}/movies.csv", index=False)
    
    print(f" {len(all_movies)} films enregistrés dans data/movies.csv")

if __name__ == "__main__":
    fetch_movies()