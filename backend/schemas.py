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