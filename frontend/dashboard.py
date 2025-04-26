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
from pathlib import Path


st.set_page_config(page_title="Homeflix : Tableau de Bord", layout="centered")
st.title(" Homeflix : Tableau de Bord")


conn = duckdb.connect('data/movies.db',  read_only=True)

# Chargement des données
ratings_df = conn.execute("SELECT user_id, film_id, rating FROM ratings").df()
movies_df = conn.execute("SELECT * FROM movies").df()



st.sidebar.title("Navigateur")
choice = st.sidebar.radio("Sélectionnez une section", ["Accueil", 
                                                      "Distribution Des Notes Moyennes", 
                                                     "Evolution De La Fréquence Annuel Des Films",
                                                     "Fréquence Des Films Par Genre",
                                                     "Activité D’un Utilisateur",
                                                     "Statistiques Par Genre Et Année",
                                                     "Outils De Recommandations Personnalisées",
                                                     "A Propos Du Projet Homeflix"]) 


if choice== "Accueil":
    
    st.subheader("🏡 Accueil")
    try:
        with open("../README.md", "r", encoding="utf-8") as f:
            contenu = f.read()
        st.markdown(contenu, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("README.md non trouvé")


elif choice == "Distribution Des Notes Moyennes":
    st.subheader("Distribution Des Notes Moyennes")
    st.write("Distribution globale des notes moyennes données aux films par les utilisateurs de la plateforme TMDB.")
    hist_values=np.histogram(movies_df["vote_average"])[0]
    st.bar_chart(hist_values, color="#9370DB")


elif choice == "Evolution De La Fréquence Annuel Des Films":
    st.subheader("〽️ Evolution De La Fréquence Annuel Des Films")
    st.write("Histogramme de la frequence des films sortis au cours des années.")
    if 'release_date' in movies_df.columns:
        # Conversion en datetime
        movies_df["release_date"] = pd.to_datetime(movies_df["release_date"], errors="coerce")
        # Extraction de l'année
        movies_df["release_date"] = movies_df["release_date"].dt.year
        films_par_annee = movies_df["release_date"].value_counts().sort_index()
        st.bar_chart(films_par_annee)
    else:
        st.warning("La colonne 'release_date' n'existe pas dans la table des films.")



    
elif choice == "Fréquence Des Films Par Genre":
    st.subheader("🎭 Fréquence Des Films Par Genre")
    st.write("Histogramme de la répartition des films selon les genres cinématographiques ")
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


elif choice=="Activité D’un Utilisateur":
    st.subheader("👩‍💻 Activité D’un Utilisateur")
    st.write("""En entrant un ID utilisateur (un nombre entre 1 et 270896) puis en cliquant sur "Obtenir les activités de l'utilisateur" vous obtiendrez :\n
   - le graphe de la répartion des notes moynnes attribuées par cet utilisateur,\n
   - le nombre total de notes qu'il a attribué ainsi que\n
   - la moyenne de ces attributions de notes.""")
    ratings_df=conn.execute("SELECT user_id, rating FROM ratings").df() 
    user_saisi=st.text_input("Entrez l'ID de l'utilisateur :", "")
    if st.button("Obtenir les activités de l'utilisateur") and user_saisi:
        try:
            user_saisi_int=int(user_saisi)
            if user_saisi_int in ratings_df["user_id"].unique().astype(int):
                user_ratings=ratings_df[ratings_df["user_id"] == user_saisi]
                hist_data=user_ratings["rating"].value_counts().sort_index()
                st.title("Réparition des notes moyennes")
                st.line_chart(hist_data,color="#ff798c")
                moyenne=user_ratings["rating"].astype(float).mean()
                total=len(user_ratings["rating"])
                st.write("Nombre de notes attribuées :", total)
                st.write("Moyenne des notes attribuées :", moyenne)
            else:
                st.warning("L'ID de l'utilisateur n'existe pas.")
        except ValueError:
            st.error("Veuillez entrer un ID utilisateur valide (un entier).")



elif choice=="Statistiques Par Genre Et Année" :
    st.subheader("📊 Statistiques Par Genre Et Année")
    st.write("Entrez un genre (par exemple Action, Drama, Thriller, Comedy mais le " \
    "nom de genre doit etre en anglais) et une année (entre 1933 et 2026). " \
    "Vous obtenez ainsi les meilleurs films pour le genre et l'année choisis mais " \
    "également la distribution des genres cinématographiques pour l'année demandée.")

    # --- Inputs utilisateur ---
    genre = st.text_input("Entrez un genre :", value="Action")
    year = st.number_input("Choisissez une année:", min_value=1900, max_value=2100, step=1, value=2000)

    if st.button("Afficher les statistiques"):
        try:
            url = f"http://backend:8000/statistics/{genre}/{year}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()['resultat']

                st.markdown(f"### 🎬 Top films {genre.title()} en {year}")
                best_films_df = pd.DataFrame(data["best_films"])
                if not best_films_df.empty:
                    st.table(best_films_df)
                else:
                    st.warning("Aucun film trouvé pour ces critères.")

                st.markdown("### 🎭 Distribution des genres")
                genre_dist_df = pd.DataFrame(data["distribution_genres"])
                chart = alt.Chart(genre_dist_df).mark_bar().encode(
                    x=alt.X("genres", sort='-y'),
                    y="nombre",
                    tooltip=["genres", "nombre"]
                ).properties(width=700, height=400)
                st.altair_chart(chart)

            else:
                st.error(f"Erreur {response.status_code} : {response.text}")
        except Exception as e:
            st.error(f"Erreur lors de l'appel API : {e}")


elif choice=="Outils De Recommandations Personnalisées" :
    st.subheader("🎯 Recommandations Personnalisées")
    st.write("Entrez un ID utilisateur et recevez la liste personnalisée des " \
    "recommandations de films obtenue par filtrage collaboratif et modèle SVD. " \
    "Sur cette liste de recommandations figure egalement la prediction des notes " \
    "que l'utilisateur attribuerait à chacun des films qui lui sont recommandés.\n" \
    "Liste non exhaustive d'ID valides à tester : `6, 47, 73, 343, 971, 1328, 1411, 2568, 2609`")

    user_id = st.number_input("Entrez un ID utilisateur :", min_value=1, step=1)

    if st.button("Obtenir les recommandations") and user_id:
        try:
            # Appel à l'API backend
            response = requests.post(
                f"http://backend:8000/recommandation/{user_id}"  # Remplace par ton URL si besoin
            
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


elif choice== "A Propos Du Projet Homeflix" :
    st.subheader("❔ À Propos Du Projet Homeflix")
    try:
        with open("../CONSIGNE.md", "r", encoding="utf-8") as f:
            contenu = f.read()
        st.markdown(contenu, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CONSIGNE.md non trouvée")


logger.info("Application terminée")


conn.close()
