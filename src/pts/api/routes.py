import time
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from pts.api.models import PredictionRequest, PredictionResponse
from pts.core.predictor import PredictiveTestSelector
from pts.utils import (
    setup_logging,
    get_prometheus_metrics,
    observe_prediction_latency,
)

setup_logging()
logger.disable("pts")
logger = logger.bind(name="api_routes")

router = APIRouter()

# Dépendance pour le sélecteur de tests (simulé)
def get_test_selector() -> PredictiveTestSelector:
    """Fournit une instance du sélecteur de tests."""
    # Dans un cas réel, le modèle serait chargé ici
    return PredictiveTestSelector(threshold=0.6)


@router.post("/predict", response_model=PredictionResponse)
async def predict_tests(
    request: PredictionRequest, selector: PredictiveTestSelector = Depends(get_test_selector)
) -> PredictionResponse:
    """
    Endpoint pour prédire les tests pertinents à exécuter.
    """
    start_time = time.time()
    logger.info(f"Requête de prédiction reçue pour le commit: {request.commit_hash}")

    # 1. Extraction des caractéristiques (simulée)
    # Dans un cas réel, on utiliserait les données de la requête (commit_hash, changed_files)
    # pour extraire les caractéristiques pertinentes (churn, historique d'échec, etc.)
    try:
        # Création d'un DataFrame de caractéristiques factices pour la démonstration
        features_data = {
            "test_id": [f"test_{i}" for i in range(10)],
            "feature_churn": [10, 50, 20, 100, 5, 15, 30, 60, 25, 40],
            "feature_history": [0.1, 0.5, 0.2, 0.9, 0.05, 0.15, 0.3, 0.6, 0.25, 0.4],
            "feature_complexity": [2, 5, 1, 8, 1, 3, 2, 6, 4, 3],
        }
        features_df = pd.DataFrame(features_data)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des caractéristiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la préparation des données.")

    # 2. Exécution du pipeline de prédiction
    selected_tests: List[str] = selector.run_prediction_pipeline(features_df)

    end_time = time.time()
    prediction_time_ms = (end_time - start_time) * 1000
    observe_prediction_latency(end_time - start_time)

    logger.info(f"Prédiction terminée en {prediction_time_ms:.2f} ms. {len(selected_tests)} tests sélectionnés.")

    return PredictionResponse(
        selected_tests=selected_tests,
        prediction_time_ms=prediction_time_ms,
        model_version="xgboost-v1.0",  # Version du modèle à récupérer dynamiquement
    )


from fastapi import Response

@router.get("/metrics")
async def get_metrics():
    """
    Endpoint pour les métriques Prometheus.
    """
    return Response(content=get_prometheus_metrics(), media_type="text/plain; version=0.0.4; charset=utf-8")
    
@router.get("/health")
async def health_check() -> dict:
    """
    Endpoint de vérification de l'état de santé de l'API.
    """
    return {"status": "ok", "version": "0.1.0", "model_status": "loaded"}
