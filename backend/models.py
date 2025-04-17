import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
import duckdb
from sklearn.preprocessing import MinMaxScaler
from backend.schemas import ReponseDeRecommandation



# def recommend_movies(user_id):
#     if user_id not in pred_df.index:
#         print(f"L'utilisateur {user_id} n'existe pas dans les prédictions.")
#         return []
    
#     predictions = pred_df.loc[user_id]
#     films_deja_notes = ratings_df[ratings_df['user_id'] == user_id]['film_id'].tolist()
#     vrai_predictions = predictions.drop(index=films_deja_notes) #On garde seulement les films non notés

#     if vrai_predictions.empty:
#         print(f"Aucune recommandation disponible pour l'utilisateur {user_id}.")
#         return []

#     top10 = vrai_predictions.sort_values(ascending=False).head(10) #On garde le top 10 des recommandations

#     reco_df = pd.DataFrame({
#         'film_id': top10.index,
#         'predicted_rating': top10.values
#     })

#     reco_df['film_id'] = reco_df['film_id'].astype(int) #Sécurité
#     movies_df['id'] = movies_df['id'].astype(int) #Sécurité

#     reco_df2 = reco_df.merge(movies_df, left_on='film_id', right_on='id', how='left')
#     reco_df2=reco_df2[['film_id', 'predicted_rating','title']]
#     print(reco_df2)
#     print(int(reco_df2['film_id'][1]))
#     recommandations=[]
#     for i in range(10): #Passage en liste de Recommandation
#         recommandations = recommandations.append(
#             ReponseDeRecommandation(
#             id=int(reco_df2['film_id'][i]),
#             title=reco_df2['title'][i],
#             rating_predicted=float(reco_df2['predicted_rating'][i])
#         )
#         )
#         #Recommande

#     return recommandations
    
from backend.schemas import ReponseDeRecommandation, ItemDeRecommandation

def recommend_movies(user_id: int) -> ReponseDeRecommandation:
    conn = duckdb.connect("data/movies.db")

    ratings_df = conn.execute("SELECT user_id, film_id, rating FROM ratings").df()
    movies_df = conn.execute("SELECT id, title FROM movies").df()
    ratings_df = ratings_df[ratings_df["user_id"].isin(ratings_df["user_id"].unique()[:10000])]
    ratings_df["film_id"] = ratings_df["film_id"].astype(int) #Sécurité
    movies_df["id"] = movies_df["id"].astype(int) #Sécurité
    ratings_df["user_id"] =  ratings_df["user_id"].astype(int)#sara
    ratings_df = ratings_df[ratings_df["film_id"].isin(movies_df["id"])] #On garde les notes des films qui sont dans notre base

    ratings_df["rating"] = ratings_df["rating"].astype(float) #Sécurité

    merged_df = ratings_df.merge(movies_df, left_on='film_id', right_on='id', how='left') #Merge pour avoir le nom des films    
    print(merged_df)
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
        print(f"L'utilisateur {user_id} n'existe pas dans les prédictions.")
        return ReponseDeRecommandation(id=user_id, recommandation=[])

    predictions = pred_df.loc[user_id]
    films_deja_notes = ratings_df[ratings_df['user_id'] == user_id]['film_id'].tolist()
    vrai_predictions = predictions.drop(index=films_deja_notes)

    if vrai_predictions.empty:
        print(f"Aucune recommandation disponible pour l'utilisateur {user_id}.")
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

    return ReponseDeRecommandation(
        id=user_id,
        recommandation=recommandations
    )
