import os
import logging
import pandas as pd
import duckdb

# Configuration
DB_PATH = "data/movies.db"
MOVIES_CSV = "data/movies.csv"
RATINGS_CSV = "data/ratings.csv"
REQUIRED_MOVIE_COLUMNS = {"id", "title", "genres", "release_date", "vote_average"}
REQUIRED_RATING_COLUMNS = {"userId", "movieId", "rating", "timestamp"}
# Configurer les logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# Vérifier que les fichiers existent
for file in [MOVIES_CSV, RATINGS_CSV]:
    if not os.path.exists(file):
        logging.error(f"Le fichier {file} est introuvable !")
        exit(1)
# Lecture sécurisée des CSV
def safe_read_csv(filepath):
    try:
        return pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        logging.warning(f"Le fichier {filepath} est vide !")
        return pd.DataFrame()
    except pd.errors.ParserError:
        logging.error(f"Problème de format dans {filepath} !")
        exit(1)
df_movies = safe_read_csv(MOVIES_CSV)
df_ratings = safe_read_csv(RATINGS_CSV)
df_ratings = df_ratings[df_ratings["userId"].isin(df_ratings["userId"].unique()[:1000])]
# Vérification des colonnes
def validate_columns(df, required_columns, filename):
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        logging.error(f"Colonnes manquantes dans {filename} : {missing_columns}")
        exit(1)
validate_columns(df_movies, REQUIRED_MOVIE_COLUMNS, MOVIES_CSV)
validate_columns(df_ratings, REQUIRED_RATING_COLUMNS, RATINGS_CSV)
# Renommer les colonnes des évaluations
df_ratings.columns = ["user_id", "film_id", "rating", "timestamp"]
# Connexion à DuckDB
conn = duckdb.connect(DB_PATH)

# Fonction pour insérer les données dans DuckDB sans doublons
def insert_dataframe(table_name, df, columns):
    # Créer la table si elle n'existe pas
    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join([f'{col} TEXT' if col != 'vote_average' else f'{col} FLOAT' for col in columns])}
        )
    ''')
    # Supprimer les doublons dans le DataFrame avant l'insertion
    if table_name == "ratings":
        df = df.drop_duplicates(subset=["user_id", "film_id"])  # Utiliser "user_id" et "film_id" pour la table ratings
        logging.info(df.dtypes)
    else:
        df = df.drop_duplicates(subset=["id"])  # Utilise "id" pour les films
        logging.info(df)
    # Insérer les données
    conn.execute(f'''
        INSERT INTO {table_name} ({', '.join(columns)})
        SELECT {', '.join(columns)}
        FROM df
    ''')
# Colonnes importantes pour la table "movies"
movie_columns = ["id", "title", "genres", "release_date", "vote_average"]
# Insérer les données
insert_dataframe("movies", df_movies, movie_columns)
insert_dataframe("ratings", df_ratings, ["user_id", "film_id", "rating", "timestamp"])
# Log des informations
logging.info(f" {len(df_movies)} films importés dans DuckDB.")
logging.info(f" {len(df_ratings)} évaluations importées dans DuckDB.")

conn.close()
