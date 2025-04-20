import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import requests
import pandas as pd
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
from loguru import logger


st.set_page_config(page_title="Homeflix Dashboard", layout="centered")
st.title(" Homeflix Dashboard")

conn = duckdb.connect('data/movies.db',  read_only=True)

# Chargement des données
ratings_df = conn.execute("SELECT user_id, film_id, rating FROM ratings").df()
movies_df = conn.execute("SELECT * FROM movies").df()








st.sidebar.title("Navigateur")
choice = st.sidebar.radio("Sélectionnez une section", ["Repartition des notes moyennes", 
                                                     "Evolution du nombre de films par année",
                                                     "Nombre de films par genre",
                                                     "Statistiques par utilisateur"
                                                     "Recommandations",
                                                     "A propos"])

if choice == "Repartition des notes moyennes":
    st.subheader("Réparition des notes moyennes")
    hist_values=np.histogram(movies_df["vote_average"])[0]
    st.bar_chart(hist_values, color="#9370DB")



elif choice == "Evolution du nombre de films par année":
    st.subheader("🎞️ Évolution du nombre de films par année")
    if 'release_date' in movies_df.columns:
        # Conversion en datetime
        movies_df["release_date"] = pd.to_datetime(movies_df["release_date"], errors="coerce")
        # Extraction de l'année
        movies_df["release_date"] = movies_df["release_date"].dt.year
        films_par_annee = movies_df["release_date"].value_counts().sort_index()
        st.bar_chart(films_par_annee)
    else:
        st.warning("La colonne 'release_date' n'existe pas dans la table des films.")



    
elif choice == "Nombre de films par genre":
    st.subheader("🎭 Nombre de films par genre")

    # Séparer les genres (séparés par virgule et éventuellement espaces)
    movies_df['genres'] = movies_df['genres'].fillna("")  # Pour éviter les NaN
    all_genres = movies_df['genres'].str.split(',\s*')  # Liste de listes

    # Aplatir la liste et compter
    from collections import Counter
    flat_genres = [genre for sublist in all_genres for genre in sublist if genre]  # Flatten + remove empty
    genre_counts = Counter(flat_genres)

    # Convertir en DataFrame
    genre_count_df = pd.DataFrame(genre_counts.items(), columns=['genre', 'nombre']).sort_values(by='nombre', ascending=False)

    st.bar_chart(genre_counts, color="#79ffdb")

elif choice== "A propos" :
    st.subheader("📘 À propos de Homeflix")
    try:
        with open("CONSIGNE.md", "r", encoding="utf-8") as f:
            contenu = f.read()
        st.markdown(contenu, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CONSIGNE.md non trouvée")

elif choice=="Statistiques par utilisateur":
    ratings_df=conn.execute("SELECT user_id, rating FROM ratings").df()
user_saisi=st.text_input("Entrez l'ID de l'utilisateur :", "")
if user_saisi:
    try:
        user_saisi_int=int(user_saisi)
        if user_saisi_int in ratings_df["user_id"].unique().astype(int):
            user_ratings=ratings_df[ratings_df["user_id"] == user_saisi]
            hist_data=user_ratings["rating"].value_counts().sort_index()
            st.title("Réparition des notes moyennes")
            st.bar_chart(hist_data,color="#FF00FF")
            moyenne=user_ratings["rating"].astype(float).mean()
            total=len(user_ratings["rating"])
            st.write("Nombre de notes attribuées :", total)
            st.write("Moyenne des notes attribuées :", moyenne)
        else:
            st.warning("L'ID de l'utilisateur n'existe pas.")
    except ValueError:
        st.error("Veuillez entrer un ID utilisateur valide (un entier).")

elif choice=="Recommandations" :
 st.subheader("🎯 Recommandation personnalisée")

 user_id = st.number_input("Entrez votre identifiant utilisateur :", min_value=1, step=1)

 if st.button("Obtenir mes recommandations") and user_id:
     try:
         # Appel à l'API backend
         response = requests.post(
             f"http://127.0.0.1:8000/recommandation/{user_id}"  # Remplace par ton URL si besoin
        
         )
         if response.status_code == 200:
             data = response.json()
             st.success(f"Recommandations pour l'utilisateur {data['id']}")

             recommandations = pd.DataFrame(data["recommandation"])
             st.dataframe(recommandations)

         else:
             st.error(f"Erreur {response.status_code} : {response.text}")

     except Exception as e:
         st.error(f"Erreur lors de l'appel API : {e}")



logger.info("Application terminée")

conn.close()