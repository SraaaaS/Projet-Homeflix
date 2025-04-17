from pydantic import BaseModel
from typing import List, Union, Optional

class Movie(BaseModel):
    id : int
    title : str    
    genres : Optional[str]

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

    # class Config:
    #     arbitrary_types_allowed = True


# from typing import List, Dict, Union
# from pydantic import BaseModel

# class Movie(BaseModel):
#     id: int
#     title: str
#     genres: str
#     vote_average: float

# class Recommandation(BaseModel):
#     user_id: int
#     recommendations: List[Dict[str, Union[str, int, float]]]

# class Statistics(BaseModel):
#     top_movies: List[Dict[str, Union[str, float]]]
#     genre_distribution: Dict[str, int]
