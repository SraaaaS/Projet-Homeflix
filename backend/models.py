import pandas as pd
import numpy as np
import duckdb
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import mean_squared_error

# Connexion à DuckDB pour récupérer les données
conn = duckdb.connect("../data/movies.db")

# Récupérer les données des évaluations et des films
ratings_df = conn.execute("SELECT user_id, film_id, rating FROM ratings").df()
movies_df = conn.execute("SELECT id, title FROM movies").df()
ratings_df = ratings_df[ratings_df["user_id"].isin(ratings_df["user_id"].unique()[:500])]

print(ratings_df)

# Créer une matrice utilisateur x film (user-item matrix)
ratings_matrix = ratings_df.pivot(index='user_id', columns='film_id', values='rating').fillna(0)
ratings_matrix.index = ratings_matrix.index.astype(str)
ratings_matrix.columns = ratings_matrix.columns.astype(str)
# Appliquer SVD (Truncated SVD)
svd = TruncatedSVD(n_components=50, random_state=42)
svd_matrix = svd.fit_transform(ratings_matrix)

def get_movie_title(movie_id):
    # On suppose que tu as un fichier CSV ou une base de données qui contient les titres des films
    # Exemple avec un fichier CSV "movies.csv" qui a des colonnes "id" et "title"
    movie_df = pd.read_csv("../data/movies.db", encoding="ISO-8859-1")  # ou utilise une autre méthode d'accès à la source des films
    # On cherche le film en fonction de son ID
    movie_title = movie_df[movie_df['id'] == int(movie_id)]['title'].values[0]
    
    return movie_title

# Fonction pour prédire une note pour un utilisateur et un film
def predict_rating(user_id: int, movie_id: int):
    # Trouver l'index de l'utilisateur et du film dans la matrice
    user_index = ratings_matrix.index.get_loc(user_id)
    movie_index = ratings_matrix.columns.get_loc(movie_id)
    
    # Calculer la prédiction en utilisant la matrice de caractéristiques SVD
    predicted_rating = np.dot(svd_matrix[user_index], svd.components_[:, movie_index])
    return predicted_rating

# Fonction pour recommander des films pour un utilisateur donné
def recommend_movies(user_id, n=5):
    user_id = str(user_id)
    recommendations = []
    
    for movie_id in ratings_matrix.columns:
        if ratings_matrix.at[user_id, movie_id] == 0:
            predicted_rating = predict_rating(user_id, movie_id)
            if predicted_rating is not None:
                recommendations.append({
                    'id': movie_id,
                    'title': get_movie_title(movie_id),
                    'rating_predicted': predicted_rating
                })

    # Trier et prendre les meilleurs
    recommendations = sorted(recommendations, key=lambda x: x['rating_predicted'], reverse=True)[:n]
    return recommendations


def get_valid_user_ids():
    return ratings_matrix.index.tolist()


conn.close()