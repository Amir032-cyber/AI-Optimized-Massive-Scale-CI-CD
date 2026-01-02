import pandas as pd
import pytest
import numpy as np

@pytest.fixture
def sample_data_for_tests():
    """Fournit un jeu de données complet pour les tests d'intégration."""
    data = {
        "commit_id": [f"hash_{i % 10}" for i in range(100)],
        "test_id": [f"test_{i % 20}" for i in range(100)],
        "test_failed": [1 if i % 15 == 0 else 0 for i in range(100)],
        "churn": np.random.randint(1, 100, 100),
        "author_experience": np.random.randint(1, 50, 100),
        "message": [f"feat: change {i}" for i in range(100)],
        "committed_date": [1672531200 + i * 3600 for i in range(100)],
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_features_for_prediction():
    """Fournit un jeu de caractéristiques pour la prédiction."""
    data = {
        "test_id": [f"test_{i}" for i in range(20)],
        "feature_churn": np.random.randint(1, 100, 20),
        "feature_history": np.random.rand(20),
        "feature_complexity": np.random.rand(20) * 10,
    }
    return pd.DataFrame(data)
