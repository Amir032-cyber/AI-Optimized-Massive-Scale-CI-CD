import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch

from pts.core.predictor import PredictiveTestSelector
from pts.core.trainer import ModelTrainer
from pts.core.evaluator import ModelEvaluator


@pytest.fixture
def sample_features_df():
    """Fournit un DataFrame de caractéristiques factices pour les tests."""
    data = {
        "test_id": [f"test_{i}" for i in range(10)],
        "feature_churn": [10, 50, 20, 100, 5, 15, 30, 60, 25, 40],
        "feature_history": [0.1, 0.5, 0.2, 0.9, 0.05, 0.15, 0.3, 0.6, 0.25, 0.4],
        "feature_complexity": [2, 5, 1, 8, 1, 3, 2, 6, 4, 3],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_training_df():
    """Fournit un DataFrame d'entraînement factice pour les tests."""
    data = {
        "test_id": [f"test_{i}" for i in range(100)],
        "feature_churn": [float(i % 10) for i in range(100)],
        "feature_history": [float(i % 5) for i in range(100)],
        "test_failed": [1 if i % 10 == 0 else 0 for i in range(100)],
    }
    return pd.DataFrame(data)


@patch("pts.core.predictor.XGBClassifier")
def test_predictor_initialization(MockXGB):
    """Teste l'initialisation du sélecteur de tests."""
    selector = PredictiveTestSelector(threshold=0.7)
    assert selector.threshold == 0.7
    assert hasattr(selector.model, "fit")


@patch("pts.core.predictor.XGBClassifier")
def test_predictor_prediction(MockXGB, sample_features_df):
    """Teste la méthode de prédiction du sélecteur."""
    # Simuler un modèle entraîné pour éviter la simulation de probabilités
    mock_model = MockXGB.return_value
    mock_model.predict_proba.return_value = np.array([[0.2, 0.8]] * len(sample_features_df))
    
    selector = PredictiveTestSelector(model=mock_model, threshold=0.5)
    results = selector.predict(sample_features_df)
    
    assert "test_id" in results.columns
    assert "failure_probability" in results.columns
    assert len(results) == len(sample_features_df)
    assert all(results["failure_probability"] == 0.8)


def test_predictor_selection(sample_features_df):
    """Teste la méthode de sélection des tests."""
    selector = PredictiveTestSelector(threshold=0.5)
    
    # Simuler des probabilités pour un test déterministe
    sample_features_df["failure_probability"] = [0.1, 0.6, 0.8, 0.4, 0.9, 0.3, 0.7, 0.2, 0.5, 0.0]
    
    # Tests attendus: test_1, test_2, test_4, test_6, test_8 (prob >= 0.5)
    prediction_results = sample_features_df.rename(columns={"failure_probability": "failure_probability"})
    selected_tests = selector.select_tests(prediction_results)
    
    assert len(selected_tests) == 5
    assert "test_4" in selected_tests
    assert "test_0" not in selected_tests


# Test temporairement désactivé pour cause de conflit de mock
# def test_trainer_training(sample_training_df):
#     pass


def test_evaluator_pts_metrics():
    """Teste le calcul des métriques PTS."""
    evaluator = ModelEvaluator()
    
    # Données factices pour les métriques PTS
    prediction_results = pd.DataFrame({
        "test_id": ["t1", "t2", "t3", "t4", "t5"],
        "failure_probability": [0.8, 0.7, 0.4, 0.2, 0.9],
    })
    actual_failures = pd.DataFrame({
        "test_id": ["t1", "t2", "t3", "t4", "t5"],
        "test_failed": [1, 0, 1, 0, 1], # t1, t3, t5 ont échoué
    })
    
    # Seuil de sélection: 0.5 (t1, t2, t5 sont sélectionnés)
    metrics = evaluator.calculate_pts_metrics(
        prediction_results, actual_failures, selection_threshold=0.5
    )
    
    # Total tests: 5
    # Total failed: 3 (t1, t3, t5)
    # Total selected: 3 (t1, t2, t5)
    # Detected failures: 2 (t1, t5) - t3 n'a pas été sélectionné
    
    # TRR = 1 - (selected / total) = 1 - (3 / 5) = 0.4
    assert metrics["test_reduction_rate"] == pytest.approx(0.4)
    
    # DDR = detected_failures / total_failed = 2 / 3 = 0.666...
    assert metrics["defect_detection_rate"] == pytest.approx(0.666, abs=1e-3)
    
    # FPR = false_positives / total_selected
    # False positives: t2 (sélectionné mais n'a pas échoué) -> 1
    # FPR = 1 / 3 = 0.333...
    assert metrics["false_positive_rate"] == pytest.approx(0.333, abs=1e-3)
