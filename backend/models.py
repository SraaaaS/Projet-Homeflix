import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
import duckdb
from sklearn.preprocessing import MinMaxScaler
from schemas import ReponseDeRecommandation, ItemDeRecommandation
from loguru import logger
import traceback


def recommend_movies(user_id: int) -> ReponseDeRecommandation:
    
    try:
        logger.info(f"Connexion à la base de données pour générer une recommandation pour user_id={user_id}")
        conn = duckdb.connect("data/movies.db",read_only=True)

        ratings_df = conn.execute("SELECT * FROM ratings").df()
        movies_df = conn.execute("SELECT * FROM movies").df()
        logger.success(f"Chargement terminé : {len(ratings_df)} ratings et {len(movies_df)} films récupérés")

        
        ratings_df = ratings_df[ratings_df["user_id"].isin(ratings_df["user_id"].unique()[:1000])]
        ratings_df["film_id"] = ratings_df["film_id"].astype(int) #Sécurité
        movies_df["id"] = movies_df["id"].astype(int) #Sécurité 
        ratings_df["user_id"] =  ratings_df["user_id"].astype(int)#sara
        ratings_df = ratings_df[ratings_df["film_id"].isin(movies_df["id"])] #On garde les notes des films qui sont dans notre base

        ratings_df["rating"] = ratings_df["rating"].astype(float) #Sécurité

        merged_df = ratings_df.merge(movies_df, left_on='film_id', right_on='id', how='left') #Merge pour avoir le nom des films    
        logger.info(f"Matrice de notes créée avec {merged_df['user_id'].nunique()} utilisateurs")

        ratings_matrix = ratings_df.pivot_table(index='user_id', columns='film_id', values='rating').fillna(0) #Matrice userxfilm avec des 0 quand pas de note

        #Partie application SVD
        svd = TruncatedSVD(n_components=14, random_state=42) 
        matrice_latente = svd.fit_transform(ratings_matrix)
        U_sig = matrice_latente                  
        V_trans = svd.components_               
        predicted_ratings = np.dot(U_sig, V_trans)

        #On met en dataframe pour plus de clarté
        pred_df = pd.DataFrame(predicted_ratings, index=ratings_matrix.index, columns=ratings_matrix.columns)

        #On va juste réajuster les valeurs car ya des négatives etcc sur l'échelle de note 0 a 5
        scaler = MinMaxScaler(feature_range=(0, 10))
        pred_df_scaled = pd.DataFrame(scaler.fit_transform(pred_df), index=pred_df.index, columns=pred_df.columns)
        pred_df = pred_df_scaled

            
        print(pred_df.index.tolist()[:10])

        if user_id not in pred_df.index:
            logger.warning(f"L'utilisateur {user_id} n'a pas de prédictions disponibles")
            return ReponseDeRecommandation(id=user_id, recommandation=[])

        predictions = pred_df.loc[user_id]
        films_deja_notes = ratings_df[ratings_df['user_id'] == user_id]['film_id'].tolist()
        vrai_predictions = predictions.drop(index=films_deja_notes)

        if vrai_predictions.empty:
            logger.warning(f"Aucune recommandation possible pour l'utilisateur {user_id} (a tout noté)")
            return ReponseDeRecommandation(id=user_id, recommandation=[])

        top10 = vrai_predictions.sort_values(ascending=False).head(10)

        reco_df = pd.DataFrame({
            'film_id': top10.index,
            'predicted_rating': top10.values
        })

        reco_df['film_id'] = reco_df['film_id'].astype(int)
        reco_df2 = reco_df.merge(movies_df, left_on='film_id', right_on='id', how='left')
        reco_df2 = reco_df2[['film_id', 'predicted_rating', 'title']]

        recommandations = []
        for i in range(len(reco_df2)):
            recommandations.append(ItemDeRecommandation(
                title=reco_df2['title'].iloc[i],
                rating_predicted=float(reco_df2['predicted_rating'].iloc[i])
            ))

        logger.success(f"{len(recommandations)} recommandations générées pour user_id={user_id}")

        #conn.close() #il faut fermer les connexions tchip

        return ReponseDeRecommandation(
            id=user_id,
            recommandation=recommandations
        )

        

    except Exception as e:
        logger.error(f"Erreur inattendue lors de la génération de recommandations pour user_id={user_id}: {traceback.format_exc()}")
        raise

    