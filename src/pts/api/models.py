from typing import List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """
    Modèle de requête pour la prédiction de tests.
    """
    commit_hash: str = Field(
        ...,
        description="Le hash du commit pour lequel la sélection de tests doit être effectuée.",
        example="a1b2c3d4e5f67890",
    )
    repository_url: str = Field(
        ...,
        description="L'URL du dépôt Git.",
        example="https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD",
    )
    changed_files: Optional[List[str]] = Field(
        None,
        description="Liste optionnelle des fichiers modifiés dans ce commit.",
        example=["src/pts/core/predictor.py", "tests/unit/test_core.py"],
    )


class PredictionResponse(BaseModel):
    """
    Modèle de réponse pour la prédiction de tests.
    """
    selected_tests: List[str] = Field(
        ...,
        description="Liste des identifiants des tests recommandés pour l'exécution.",
        example=["test_core.test_predictor_init", "test_data.test_collector_commit"],
    )
    prediction_time_ms: float = Field(
        ...,
        description="Temps pris pour la prédiction en millisecondes.",
        example=52.45,
    )
    model_version: str = Field(
        ...,
        description="Version du modèle ML utilisé pour la prédiction.",
        example="xgboost-v1.2",
    )


class HealthCheckResponse(BaseModel):
    """
    Modèle de réponse pour le statut de santé de l'API.
    """
    status: str = Field(..., example="ok")
    version: str = Field(..., example="0.1.0")
    model_status: str = Field(..., example="loaded")
