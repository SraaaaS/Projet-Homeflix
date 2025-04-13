from fastapi import FastAPI
from backend.routes import router

app = FastAPI(
    title = "API du Projet Homeflix",
    description = "API REST pour la gestion des films et recommandations et quelques statistics",
    version = "1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message" : "Bienvenue sur l'API Homeflix"}
