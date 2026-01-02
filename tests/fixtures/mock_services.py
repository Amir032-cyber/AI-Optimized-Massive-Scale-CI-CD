import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_github_integration():
    """Mock l'intégration GitHub pour éviter les appels réseau réels."""
    with patch("pts.integrations.github.GitHubIntegration") as MockIntegration:
        instance = MockIntegration.return_value
        instance.get_commit_details.return_value = {
            "sha": "mock_sha",
            "author": "Mock User",
            "date": "2023-01-01",
            "message": "Mock commit",
            "changed_files": ["file1.py", "file2.py"],
        }
        instance.get_pull_request_files.return_value = ["file3.py", "file4.py"]
        yield instance

@pytest.fixture
def mock_ml_model():
    """Mock un modèle ML pour les tests de l'API."""
    with patch("pts.core.predictor.XGBClassifier") as MockModel:
        instance = MockModel.return_value
        # Simuler la méthode predict_proba pour retourner des probabilités
        instance.predict_proba.return_value = [[0.2, 0.8], [0.9, 0.1]] * 5 # 10 tests
        yield instance
