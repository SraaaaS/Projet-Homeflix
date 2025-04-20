from fastapi import APIRouter, FastAPI
from typing import List, Optional, Dict
import pandas as pd
import duckdb   

from backend.models import recommend_movies
from backend.schemas import Movie, ReponseDeRecommandation, Statistics, Top_Movies, Genre_Distrib

from fastapi import HTTPException
import traceback

app = FastAPI()
router = APIRouter()

DB_PATH = "data/movies.db"  
conn = duckdb.connect(DB_PATH, read_only=True)


@router.get('/movies', response_model=Dict[str,List[Movie]])
def get_movie():
    requete = "SELECT id, title, genres FROM movies"
    dataset = conn.execute(requete).df()
    return {"Liste des films": dataset.to_dict(orient='records')}




@router.post("/recommandation/{id_user}", response_model=ReponseDeRecommandation)
def post_recommandations(id_user : int):    
    
    liste_de_recommandations = recommend_movies(id_user) #la fonction realisant les recmmandations

   
    return liste_de_recommandations 


@router.get("/statistics/{genres}/{year}", response_model=Dict[str, Statistics])
def get_statistics(genres : str, year : int):

    #ajout de condition sur la date de sortie des films considérés par rapport à l'énoncé
    # requete_meilleurs_films = f"""
    # SELECT title, vote_average
    # FROM movies 
    # WHERE strftime('%Y', CAST(release_date AS DATE) )= '{year}'
    # ORDER BY vote_average DESC
    # LIMIT 10
    # """

    requete_meilleurs_films = f"""
    SELECT title, vote_average AS rating_average
    FROM movies 
    WHERE strftime('%Y', CAST(release_date AS DATE)) = '{year}'
    AND LOWER(genres) LIKE '%{genres.lower()}%'
    ORDER BY vote_average DESC
    LIMIT 10
    """

    requete_distrib_genres_films = """
        SELECT genre AS genres, COUNT(*) AS nombre
    FROM (
        SELECT UNNEST(STR_SPLIT(REPLACE(genres, '|', ', '), ', ')) AS genre
        FROM movies
        WHERE genres IS NOT NULL
    )
    GROUP BY genre
    ORDER BY nombre DESC
    """
    
    
    best_films = conn.execute(requete_meilleurs_films).df()
    genre_distrib = conn.execute(requete_distrib_genres_films).df()

    return {"resultat": {"genres" : genres, 
            "year" : year,
             "best_films" :  best_films.to_dict(orient="records"),
             "distribution_genres" : genre_distrib.to_dict(orient="records") }
            }

#app.include_router(router)