import pandas as pd
import pytest

from pts.features.extractor import FeatureExtractor
from pts.features.engineer import FeatureEngineer
from pts.features.selector import FeatureSelector


@pytest.fixture
def sample_merged_df():
    """Fournit un DataFrame fusionné factice pour l'extraction."""
    data = {
        "commit_id": [f"hash_{i % 10}" for i in range(20)],
        "test_id": [f"test_{i % 5}" for i in range(20)],
        "test_failed": [1 if i % 5 == 0 else 0 for i in range(20)],
        "churn": [10, 50, 20, 100, 5] * 4,
        "author_experience": [10, 5, 5, 5, 5] * 4,
        "message": ["feat: a", "fix: b", "docs: c", "feat: d", "fix: e"] * 4,
    }
    return pd.DataFrame(data)


def test_extractor_test_features(sample_merged_df):
    """Teste l'extraction des caractéristiques liées aux tests."""
    extractor = FeatureExtractor()
    features_df = extractor.extract_test_features(sample_merged_df)
    
    assert "historical_failure_rate" in features_df.columns
    
    # Vérifier que le taux d'échec historique est correct pour un test
    # test_0 échoue à chaque fois dans ce mock simplifié (test_failed est 1 si i % 5 == 0, et test_id est test_{i % 5})
    # Donc pour test_0, i peut être 0, 5, 10, 15 -> tous échouent.
    test_0_rate = features_df[features_df["test_id"] == "test_0"]["historical_failure_rate"].iloc[0]
    assert test_0_rate == pytest.approx(1.0)
    
    # test_1 n'échoue jamais -> 0.0
    test_1_rate = features_df[features_df["test_id"] == "test_1"]["historical_failure_rate"].iloc[0]
    assert test_1_rate == pytest.approx(0.0)


def test_engineer_interaction_features():
    """Teste la création des caractéristiques d'interaction."""
    engineer = FeatureEngineer()
    
    data = {
        "churn": [10, 50, 0, 100],
        "historical_failure_rate": [0.1, 0.5, 0.2, 0.9],
        "author_experience": [5, 10, 2, 20],
    }
    df = pd.DataFrame(data)
    
    engineered_df = engineer.create_interaction_features(df)
    
    assert "churn_failure_interaction" in engineered_df.columns
    assert engineered_df["churn_failure_interaction"].iloc[0] == pytest.approx(1.0) # 10 * 0.1
    assert engineered_df["churn_failure_interaction"].iloc[1] == pytest.approx(25.0) # 50 * 0.5
    
    assert "exp_churn_ratio" in engineered_df.columns
    assert engineered_df["exp_churn_ratio"].iloc[2] == pytest.approx(2.0) # Division par zéro gérée (retourne author_experience)


def test_engineer_categorical_encoding():
    """Teste l'encodage des caractéristiques catégorielles."""
    engineer = FeatureEngineer()
    
    data = {
        "commit_id": ["a", "b", "c", "d"],
        "test_id": ["t1", "t2", "t3", "t4"],
        "test_failed": [0, 1, 0, 1],
        "churn": [10, 50, 20, 100],
        "author_experience": [5, 10, 2, 20],
        "historical_failure_rate": [0.1, 0.5, 0.2, 0.9],
        "message": ["feat: a", "fix: b", "docs: c", "feat: d"],
    }
    df = pd.DataFrame(data)
    df = engineer.create_interaction_features(df)
    
    # Simuler l'extraction du type de commit
    def get_commit_type(message: str) -> str:
        if message.startswith("feat"):
            return "feature"
        elif message.startswith("fix"):
            return "fix"
        elif message.startswith("docs"):
            return "docs"
        else:
            return "other"
    df["commit_type"] = df["message"].apply(get_commit_type)
    
    engineered_df = engineer.encode_categorical_features(df)
    
    assert "commit_type" not in engineered_df.columns
    assert "type_feature" in engineered_df.columns
    assert "type_fix" in engineered_df.columns
    assert "type_docs" in engineered_df.columns
    assert engineered_df["type_feature"].iloc[0] == 1
    assert engineered_df["type_fix"].iloc[0] == 0


def test_selector_k_best():
    """Teste la sélection des K meilleures caractéristiques."""
    config = {"k_best": 2, "target_column": "target"}
    selector = FeatureSelector(config=config)
    
    # Créer un DataFrame où 'good_feature' est fortement corrélé à 'target'
    data = {
        "commit_id": ["a", "b", "c", "d"],
        "test_id": ["t1", "t2", "t3", "t4"],
        "target": [0, 1, 0, 1],
        "good_feature": [0.1, 0.9, 0.2, 0.8],
        "bad_feature": [0.5, 0.5, 0.5, 0.5],
        "medium_feature": [0.3, 0.7, 0.4, 0.6],
    }
    df = pd.DataFrame(data)
    
    selected_df = selector.select_k_best(df)
    
    # On s'attend à ce que 'good_feature' et 'medium_feature' soient sélectionnés
    assert len(selector.selected_features) == 2
    assert "good_feature" in selector.selected_features
    assert "bad_feature" not in selector.selected_features
    assert "target" in selected_df.columns
    assert "bad_feature" not in selected_df.columns
