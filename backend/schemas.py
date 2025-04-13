from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    id : int
    title : str
    genre : str
    release_date : str
    vote_average : float


class Recommandation(BaseModel):
    id : int
    title : str
    rating_predicted : float
    

class Top_Movies(BaseModel):
    title : str
    rating_average : float

class Genre_Distrib(BaseModel):
    genre : str
    nombre : int

class Statistics(BaseModel):
    genre : str
    year : int
    best_films = List[Top_Movies]
    distribution_genres = List[Genre_Distrib]

