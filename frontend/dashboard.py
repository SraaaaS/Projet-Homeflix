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

# Logs visuels pour Streamlit
visual_logs = []
def visual_log(message: str, level: str = "INFO"):
    if level == "INFO":
        color = "#66B2FF"
    elif level == "SUCCESS":
        color = "#77DD77"
    elif level == "WARNING":
        color = "orange"
    elif level == "ERROR":
        color = "red"
    else:
        color = "black"

    visual_logs.append(f"<span style='color:{color};'>[{level}] {message}</span>")

    if len(visual_logs) > 20:
        visual_logs.pop(0)


logger.info("Démarrage de l'application Streamlit Homeflix")
visual_log(f"Démarrage de l'application Streamlit Homeflix", "INFO")

st.set_page_config(page_title="Homeflix : Tableau de Bord", layout="centered")
st.title(" Homeflix : Tableau de Bord")

try:
    logger.success("Connexion réussie à la base de données movies.db")
    visual_log(f"Connexion réussie à la base de données movies.db", "SUCCESS")
    conn = duckdb.connect('data/movies.db',  read_only=True)
except Exception as e:
    logger.error(f"Erreur de connexion à DuckDB : {e}")

# Chargement des données
try:
    ratings_df = conn.execute("SELECT user_id, film_id, rating FROM ratings").df()
    movies_df = conn.execute("SELECT * FROM movies").df()
    logger.success(f"{len(ratings_df)} ratings et {len(movies_df)} films chargés avec succès")

except Exception as e:
    logger.error(f"Erreur lors du chargement des données : {e}")
    visual_log(f"Erreur lors du chargement des données : {e}", "ERROR")

st.sidebar.title("Navigateur")
choice = st.sidebar.radio("Sélectionnez une section", ["Accueil", 
                                                      "Distribution Des Notes Moyennes", 
                                                     "Evolution De La Fréquence Annuelle Des Films",
                                                     "Fréquence Des Films Par Genre",
                                                     "Activité D’un Utilisateur",
                                                     "Statistiques Par Genre Et Année",
                                                     "Outils De Recommandations Personnalisées",
                                                     "A Propos Du Projet Homeflix"]) 
logger.info(f"Section sélectionnée par l'utilisateur : {choice}")
visual_log(f"Section sélectionnée par l'utilisateur : {choice}", "INFO")

if choice== "Accueil":
    
    st.subheader("🏡 Accueil")
    
    # try:
    #     with open("../README.md", "r", encoding="utf-8") as f:
    #         contenu = f.read()
    #     st.markdown(contenu, unsafe_allow_html=True)
    
    # except FileNotFoundError:
    #     st.error("README.md non trouvé")

    try:
        with open("../README.md", "r", encoding="utf-8") as f:
            contenu = f.read()

        # Remplacer les chemins d'images relatifs par des liens GitHub RAW
        contenu = contenu.replace(
            "images/",
            "https://raw.githubusercontent.com/SraaaaS/Projet-Homeflix/docs/images-readme/images/"
        )

        # Afficher le README avec Streamlit
        st.markdown(contenu, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error("README.md non trouvé.")


    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)

elif choice == "Distribution Des Notes Moyennes":
    st.subheader("Distribution Des Notes Moyennes")
    st.write("Distribution globale des notes moyennes données aux films par les utilisateurs de la plateforme TMDB.")
    hist_values=np.histogram(movies_df["vote_average"])[0]
    st.bar_chart(hist_values, color="#9370DB")

    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)


elif choice == "Evolution De La Fréquence Annuelle Des Films":
    st.subheader("〽️ Evolution De La Fréquence Annuelle Des Films")
    st.write("Histogramme de la fréquence des films sortis au cours des années.")
    if 'release_date' in movies_df.columns:
        # Conversion en datetime
        movies_df["release_date"] = pd.to_datetime(movies_df["release_date"], errors="coerce")
        # Extraction de l'année
        movies_df["release_date"] = movies_df["release_date"].dt.year
        films_par_annee = movies_df["release_date"].value_counts().sort_index()
        st.bar_chart(films_par_annee)
    else:
        st.warning("La colonne 'release_date' n'existe pas dans la table des films.")

    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)



    
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

    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)


elif choice=="Activité D’un Utilisateur":
    st.subheader("👩‍💻 Activité D’un Utilisateur")
    st.write("""En entrant un ID utilisateur (un nombre entre 1 et 270896) puis en cliquant sur "Obtenir les activités de l'utilisateur" vous obtiendrez :\n
   - le graphe de la répartition des notes moyennes attribuées par cet utilisateur,\n
   - le nombre total de notes qu'il a attribuées\n
   - la moyenne de ces attributions de notes.""")
    ratings_df=conn.execute("SELECT user_id, rating FROM ratings").df() 
    user_saisi=st.text_input("Entrez l'ID de l'utilisateur :", "")

    if st.button("Obtenir les activités de l'utilisateur") and user_saisi:
        logger.info(f"Utilisateur a saisi : {user_saisi}")
        visual_log(f"Utilisateur a saisi : {user_saisi}", "INFO")

        try:
            user_saisi_int=int(user_saisi)

            if user_saisi_int in ratings_df["user_id"].unique().astype(int):
                logger.success(f"Activité trouvée pour user_id={user_saisi_int}")
                user_ratings=ratings_df[ratings_df["user_id"] == user_saisi]
                hist_data=user_ratings["rating"].value_counts().sort_index()
                st.title("Répartition des notes moyennes")
                st.line_chart(hist_data,color="#ff798c")
                moyenne=user_ratings["rating"].astype(float).mean()
                total=len(user_ratings["rating"])
                st.write("Nombre de notes attribuées :", total)
                st.write("Moyenne des notes attribuées :", moyenne)
                
            else:
                st.warning("L'ID de l'utilisateur n'existe pas.")
                logger.warning(f"ID utilisateur invalide saisi : {user_saisi}")

        except ValueError:
            st.error("Veuillez entrer un ID utilisateur valide (un entier).")

    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)


elif choice=="Statistiques Par Genre Et Année" :
    st.subheader("📊 Statistiques Par Genre Et Année")
    st.write("Entrez un genre (par exemple Action, Drama, Thriller, Comedy mais le " \
    "nom de genre doit etre en anglais) et une année (entre 1933 et 2026). " \
    "Vous obtenez ainsi les meilleurs films pour le genre et l'année choisis mais " \
    "également la distribution des genres cinématographiques pour l'année demandée.")

    # --- Inputs utilisateur ---
    genre = st.text_input("Entrez un genre :", value="Action")
    year = st.number_input("Choisissez une année:", min_value=1933, max_value=2026, step=1, value=2000)

    if st.button("Afficher les statistiques"):
        logger.info(f"Demande de stats pour genre={genre} et année={year}")
        visual_log(f"Demande de stats pour genre={genre} et année={year}", "INFO")
        
        try:
            url = f"http://backend:8000/statistics/{genre}/{year}"
            response = requests.get(url)

            if response.status_code == 200:
                logger.success("Réponse API /statistics reçue avec succès")
                visual_log(f"Réponse API /statistics reçue avec succès", "SUCCESS")
        
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
                logger.error(f"Erreur API /statistics: {response.status_code}")
                visual_log(f"Erreur API /statistics: {response.status_code}", "ERROR")
        
                st.error(f"Erreur {response.status_code} : {response.text}")
        
        except Exception as e:
            st.error(f"Erreur lors de l'appel API : {e}")
    
    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)


elif choice=="Outils De Recommandations Personnalisées" :
    st.subheader("🎯 Recommandations Personnalisées")
    st.write("Entrez un ID utilisateur et recevez la liste personnalisée des " \
    "recommandations de films obtenue par filtrage collaboratif et modèle SVD. " \
    "Sur cette liste de recommandations figure également la prédiction des notes " \
    "que l'utilisateur attribuerait à chacun des films qui lui sont recommandés.")
    st.write(" ")
    st.write("Liste non exhaustive d'ID valides à tester : `6, 47, 73, 343, 971, 1328, 1411, 2568, 2609`")

    user_id = st.number_input("Entrez un ID utilisateur :", min_value=1, step=1)

    if st.button("Obtenir les recommandations") and user_id:
        logger.info(f"Demande de recommandations pour user_id={user_id}")
        visual_log(f"Demande de recommandations pour user_id={user_id}", "INFO")
        
        try:
            # Appel à l'API backend
            response = requests.post(
                f"http://backend:8000/recommandation/{user_id}"  # Remplace par ton URL si besoin
            
            )
            if response.status_code == 200:
                logger.success("Réponse API /recommandation reçue avec succès")
                visual_log(f"Réponse API /recommandation reçue avec succès", "SUCCESS")
        
                data = response.json()
                st.success(f"Recommandations pour l'utilisateur {data['id']}")

                recommandations = pd.DataFrame(data["recommandation"])
                st.dataframe(recommandations)

            else:
                st.error(f"Erreur {response.status_code} : {response.text}")
                logger.error(f"Erreur API /recommandation: {response.status_code}")
                visual_log(f"Erreur API /recommandation: {response.status_code}", "ERROR")
        
        except Exception as e:
            st.error(f"Erreur lors de l'appel API : {e}")

    st.markdown("---")
    st.subheader("📝 Journaux d'activité (logs)")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)


elif choice== "A Propos Du Projet Homeflix" :
    logger.info("Consultation de la page informative des consignes du projet")
    visual_log(f"Consultation de la page informative des consignes du projet", "INFO")
        
    st.subheader("❔ À Propos Du Projet Homeflix")
    
    try:
        with open("../CONSIGNE.md", "r", encoding="utf-8") as f:
            contenu = f.read()
        st.markdown(contenu, unsafe_allow_html=True)
    
    except FileNotFoundError:
        st.error("CONSIGNE.md non trouvée")

    st.markdown("---")
    st.subheader("📝 Journal d'activité")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)


logger.info("Fin de session utilisateur sur Homeflix dashboard")
visual_log(f"Fin de session utilisateur sur Homeflix dashboard", "INFO")
        
conn.close()
