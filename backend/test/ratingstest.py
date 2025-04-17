import duckdb
import pandas as pd

# Charger le CSV avec pandas
df = pd.read_csv("data/ratings.csv")

# Créer (ou ouvrir) la base de données DuckDB
con = duckdb.connect("data/ratings.db")  # Tu peux changer le chemin si tu veux

# Écrire le DataFrame dans la base de données comme table "ratings"
con.execute("DROP TABLE IF EXISTS ratings;")
con.execute("CREATE TABLE ratings AS SELECT * FROM df")

# Fermer la connexion
con.close()

print("✅ Base de données DuckDB créée avec succès dans data/ratings.db")
