from pydantic import BaseModel
from typing import List, Union, Optional
from datetime import date

class Movie(BaseModel):
    id : int
    title : str    
    genres : Optional[str]
    release_date : date
    vote_average : float

class Ratings(BaseModel):
    user_id : int
    film_id : int
    rating : float
    timestamp : int 

class ItemDeRecommandation(BaseModel):
    title : str
    rating_predicted : float
    
class ReponseDeRecommandation(BaseModel):
    id : int
    recommandation : List[ItemDeRecommandation]

class Top_Movies(BaseModel):
    title : str
    rating_average : float

class Genre_Distrib(BaseModel):
    genres : str
    nombre : int

class Statistics(BaseModel):
    genres : str
    year : int
    best_films : List[Top_Movies]
    distribution_genres : Union[Genre_Distrib, List[Genre_Distrib]]
