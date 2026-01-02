import pytest
from fastapi.testclient import TestClient

from pts.api.server import app

client = TestClient(app)


def test_health_check():
    """Teste l'endpoint de vérification de l'état de santé."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()


def test_predict_tests_success():
    """Teste l'endpoint de prédiction avec une requête valide."""
    request_data = {
        "commit_hash": "a1b2c3d4e5f67890",
        "repository_url": "https://github.com/Amir032-cyber/AI-Optimized-Massive-Scale-CI-CD",
        "changed_files": ["src/pts/core/predictor.py", "tests/unit/test_core.py"],
    }
    
    response = client.post("/api/v1/predict", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "selected_tests" in data
    assert isinstance(data["selected_tests"], list)
    assert "prediction_time_ms" in data
    assert "model_version" in data
    
    # Vérifier que la liste est retournée (peut être vide selon la simulation)
    assert isinstance(data["selected_tests"], list)


def test_predict_tests_invalid_request():
    """Teste l'endpoint de prédiction avec une requête invalide (champs manquants)."""
    request_data = {
        "commit_hash": "a1b2c3d4e5f67890",
        # 'repository_url' est manquant
    }
    
    response = client.post("/api/v1/predict", json=request_data)
    
    # FastAPI/Pydantic devrait retourner 422 Unprocessable Entity
    assert response.status_code == 422


def test_metrics_endpoint():
    """Teste l'endpoint des métriques Prometheus."""
    response = client.get("/api/v1/metrics")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    
    # Vérifier la présence de métriques PTS
    content = response.text
    assert "pts_test_reduction_rate" in content
    assert "pts_cost_savings_usd_total" in content
    assert "pts_prediction_latency_seconds" in content
