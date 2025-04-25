# Homeflix 

## Système de Recommandation de Films

Bienvenue sur Homelifx, une plateforme de recommandation de films basée sur le filtrage collaboratif, développée pour fournir à l'utilisateur une expérience personnalisée à travers l'analyse de données réelles d'autres utilisateurs. Le projet est conteneurisé avec Docker Compose et permet une visualisation interactive via une interface Streamlit.

---

### Objectifs du Projet

- Proposer des recommandations de films personnalisées basées sur les goûts d’utilisateurs similaires.
- Utiliser un modèle SVD pour ce filtrage collaboratif
- Offrir une visualisation des tendances cinématographiques avec quelques statistiques : dates de sorties, genres, notes attribuées, etc...
- Concevoir une architecture modulaire, et conteneurisée pour faciliter le déploiement de l'application

---

### Architecture globale

Le système est divisé en 3 services distincts :


- Base de données DuckDB : Stocke les films et les évaluations provenant de Kaggle et de l'API TMDB
- Backend (FastAPI) : Fournit l'API REST et intègre le modèle SVD pour les recommandations
- Frontend (Streamlit) : Interface utilisateur, visualiations

---

## Lancer le Projet


### Installation

Après avoir cloner le dépot Git, il suffira d'utiliser docker-compose de telles manière pour lancer l'application : 

`docker-compose up --build`

Ainsi l'application sera disponible à l'adresse suivante :

http://localhost:8501

### Navigation dans l'application

La barre latérale permet de choisir parmi plusieurs sections :

1. **Repartition des notes moyennes**  

    L'histogramme de la distribution globale des notes moyennes données aux films

2. **Evolution du nombre de films par année** 

    L'histogramme du nombre de films sorties chaque année

3. **Nombre de film par genre**  

    L'histogramme du nombre de films par genre

4. **Activité d’un utilisateur**  
  
    Entrez un id d'utilisateur de 1 à 270896 et les statistiques de ses notes avec le nombre de notes attribuées, sa moyenne de notes et la distribution de celles-ci

5. **Analyse par genre et par année**  

    Entrez un genre (par exemple : Action, Drama, Thriller) et une année, et obtenez les meilleurs films pour ce genre et cette année, ainsi que la distribution des genres pour cette année.  

    On utilise ici l'API :
        `GET http://backend:8000/statistics/{genre}/{year}`

6. **Recommandations**  

    Entrez un id d'utitilisateur et recevez une liste de recommandations grâce au filtrage collaboratif et SVD.  
    
    On utilise ici l'API :
        `POST HTTP://backend:8000/recommandation/{user_id}`  


    Dû à la combinaison des fichiers de ratings et de movies, les ids d'utilisateurs possibles sont plus restreints, voici une liste alétoire et non exhaustive d'id valides à tester : `6, 47, 73, 343, 971, 1328, 1411, 2568, 2609`


