import pandas as pd
import duckdb
# Afficher sous forme de tableau interactif dans VS Code
from pandasgui import show

# Connexion à la base de données
conn = duckdb.connect("data/movies.db")

# Récupérer les données sous forme de DataFrame pandas
df = conn.execute("SELECT * FROM movies").df()

# Afficher le tableau dans VS Code
print(df)  # Affichage basique dans la console

show(df)  # Ouvre une interface graphique avec le tableau

# Fermer la connexion
conn.close()
