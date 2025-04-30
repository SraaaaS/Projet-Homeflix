from fastapi import APIRouter, FastAPI
from typing import List, Optional, Dict
import pandas as pd
import duckdb   

from models import recommend_movies
from schemas import Movie, ReponseDeRecommandation, Statistics, Top_Movies, Genre_Distrib, Ratings

from fastapi import HTTPException
import traceback
from loguru import logger

app = FastAPI()
router = APIRouter()

DB_PATH = "data/movies.db"  
conn = duckdb.connect(DB_PATH, read_only=True)


@router.get('/movies', response_model=Dict[str,List[Movie]])
def get_movie():
    logger.info("Route '/movies' appelée pour récupérer la liste des films")
    requete = "SELECT * FROM movies"
    dataset = conn.execute(requete).df()
    logger.success(f"{len(dataset)} films récupérés depuis la base de données")
    return {"Liste des films": dataset.to_dict(orient='records')}


@router.get('/ratings', response_model=Dict[str,List[Ratings]])
def get_ratings():
    logger.info("Route '/ratings' appelée pour récupérer la liste des notes de films")
    requete = "SELECT * FROM ratings"
    dataset = conn.execute(requete).df()
    logger.success(f"{len(dataset)} notes de films récupérés depuis la base de données")
    return {"Liste des notes de film": dataset.to_dict(orient='records')}
 

@router.post("/recommandation/{id_user}", response_model=ReponseDeRecommandation)
def post_recommandations(id_user : int):    
    logger.info(f"Route '/recommandation/{id_user}' appelée pour générer des recommandations")
    
    try:
        liste_de_recommandations = recommend_movies(id_user) #la fonction realisant les recmmandations
        logger.success(f"Recommandations générées pour l'utilisateur {id_user}")
        return liste_de_recommandations 
    
    except Exception as e:
        logger.error(f"Erreur lors de la recommandation pour l'utilisateur {id_user} : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recommandation")
    


@router.get("/statistics/{genres}/{year}", response_model=Dict[str, Statistics])
def get_statistics(genres : str, year : int):
    logger.info(f"Route '/statistics/{genres}/{year}' appelée pour récupérer les statistiques")
    
    requete_meilleurs_films = f"""
    SELECT title, vote_average AS rating_average
    FROM movies 
    WHERE strftime('%Y', CAST(release_date AS DATE)) = '{year}'
    AND LOWER(genres) LIKE '%{genres.lower()}%'
    ORDER BY vote_average DESC
    LIMIT 10
    """

    requete_distrib_genres_films = f"""
        SELECT genre AS genres, COUNT(*) AS nombre
    FROM (
        SELECT UNNEST(STR_SPLIT(REPLACE(genres, '|', ', '), ', ')) AS genre
        FROM movies
        WHERE genres IS NOT NULL
        AND strftime('%Y', CAST(release_date AS DATE)) = '{year}'
    )
    GROUP BY genre
    ORDER BY nombre DESC
    """
    try:
        best_films = conn.execute(requete_meilleurs_films).df()
        genre_distrib = conn.execute(requete_distrib_genres_films).df()
        logger.success(f"{len(best_films)} films trouvés pour {genres} en {year}")
        logger.success(f"{len(genre_distrib)} genres comptabilisés pour l'année {year}")
        
        return {"resultat": {"genres" : genres, 
                "year" : year,
                "best_films" :  best_films.to_dict(orient="records"),
                "distribution_genres" : genre_distrib.to_dict(orient="records") }
                }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")