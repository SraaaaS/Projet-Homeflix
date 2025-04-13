from fastapi import APIRouter, FastAPI
from typing import List, Optional
import pandas as pd
import duckdb

from backend.models import recommend_movies
from backend.schemas import Movie, Recommandation, Statistics

app = FastAPI()
router = APIRouter()

DB_PATH = "data/movies.db"  
conn = duckdb.connect(DB_PATH)


@router.get('/movies/{userId}', response_model=Movie)
def get_movie(identifiant_du_film : int ):
    requete = "SELECT * FROM movies WHERE userId=?"
    #requete = "SELECT * FROM movies WHERE userId={identifiant_du_film}"
    dataset = conn.execute(requete, [identifiant_du_film]).df()
    return dataset.to_json() #a verif



@router.post("/recommandation/{id_user}", response_model=List[Recommandation])
def post_recommandations(id_user : int):    
    
    liste_de_recommandations = recommend_movies(id_user) #la fonction realisant les recmmandations
    
    #renvoyer le JSON des recommandations proposées à l'utilisateur d'identifiant id_user
    return {"identifiant_utilisateur" : id_user, "recommandations proposées" : liste_de_recommandations.sort_values(by="rating_predicted", ascending=False).head(10)}



@router.get("/statistics/{genre}/{year}", response_model=Statistics)
def get_statistics(genre : str, year : int):

    #ajout de condition sur la date de sortie des films considérés par rapport à l'énoncé
    requete_meilleurs_films = """
    SELECT title, vote_average
    FROM movies 
    WHERE release_date = {year} 
    ORDER BY vote_average DESC
    LIMIT 10
    """

    requete_distrib_genres_films = """
    SELECT genres, 
    COUNT(*) as count
    FROM( SELECT UNNEST(STRING_SPLIT(genres, "|"))
           as genres_separated
           FROM movies
        ) 
    GROUP BY genres
    ORDER BY count DESC
    """
    
    best_films = conn.execute(requete_meilleurs_films).df()
    genre_distrib = conn.execute(requete_distrib_genres_films).df()

    return {"genre du film" : genre, 
            "année de sortie" : year,
             "meilleurs films" :  best_films.to_dict(orient="records"),
             "distribution de genres" : genre_distrib.to_dict(orient="records")
            }


