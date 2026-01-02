from fastapi import FastAPI
from loguru import logger

from pts.api.routes import router as api_router
from pts.utils.logger import setup_logging

# Configuration de la journalisation
setup_logging(level="INFO")
logger.disable("pts")
logger = logger.bind(name="api_server")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Predictive Test Selection API",
    description="API pour la sélection prédictive des tests basée sur le Machine Learning.",
    version="0.1.0",
)

# Inclusion des routes
app.include_router(api_router, prefix="/api/v1", tags=["prediction"])


@app.on_event("startup")
async def startup_event() -> None:
    """
    Événement de démarrage de l'application.
    """
    logger.info("Démarrage de l'API PTS...")
    # Ici, on pourrait charger le modèle ML en mémoire
    # load_model_to_memory()
    logger.info("API PTS prête à servir les requêtes.")


@app.on_event("shutdown")
def shutdown_event() -> None:
    """
    Événement d'arrêt de l'application.
    """
    logger.info("Arrêt de l'API PTS.")


if __name__ == "__main__":
    import uvicorn
    
    # Pour le développement local
    uvicorn.run(app, host="0.0.0.0", port=8000)
