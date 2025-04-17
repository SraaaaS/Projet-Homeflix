import pandas as pd
import duckdb
# Connexion à la base de données
conn = duckdb.connect("data/movies.db")

# Récupérer les données sous forme de DataFrame pandas
df = conn.execute("SELECT * FROM movies").df()
df2 = conn.execute("SELECT * FROM ratings").df()

# Afficher le tableau dans VS Code
print(df)  # Affichage basique dans la console
print(df2) #Affichage seconde table
# Fermer la connexion
conn.close()