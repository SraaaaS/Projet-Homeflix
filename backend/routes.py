from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from typing import List, Optional
import duckdb

app = FastAPI()
router = APIRouter()

DB_PATH = "data/movies.db"  
conn = duckdb.connect(DB_PATH)

class Movie(BaseModel):
    id : int
    title : str
    genre : str
    release_date : str
    vote_average : float

@router.get('/movies/{userId}', response_model=Movie)
def get_movie(identifiant_du_film : int ):
    dataset = conn.execute("SELECT * FROM movies WHERE userId=?, [identifiant_du_film]").df()
    return dataset.to_json() #a verif




# Creation de la table de stockage des recommandations 
conn.execute("""
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    rating_predicted FLOAT
);
""")



#def get_connection():
 #   """Renvoie la connexion active à DuckDB"""
  #  return conn

class Recommandation(BaseModel):
    id : int
    title : str
    rating_predicted : float

@router.post("/recommandation/{id}", response_model=Recommandation)
def post_recommandations(id_user : int):    
    #modele de recommandation
    pass



