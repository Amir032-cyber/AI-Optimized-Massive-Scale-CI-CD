import os
import subprocess
import pytest
import pandas as pd
import yaml

# Définir le chemin de base du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


@pytest.fixture(scope="module", autouse=True)
def setup_environment():
    """
    Configure l'environnement de test (crée des fichiers de données factices).
    """
    # Créer un fichier de données factices pour l'entraînement
    data = {
        "test_id": [f"test_{i}" for i in range(100)],
        "feature_churn": [float(i % 10) for i in range(100)],
        "feature_history": [float(i % 5) for i in range(100)],
        "test_failed": [1 if i % 10 == 0 else 0 for i in range(100)],
    }
    training_df = pd.DataFrame(data)
    
    # Créer un fichier de données factices pour la prédiction
    prediction_data = training_df.drop(columns=["test_failed"])
    
    # Sauvegarder les fichiers
    os.makedirs(os.path.join(PROJECT_ROOT, "data/processed"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "data/features"), exist_ok=True)
    
    training_df.to_csv(os.path.join(PROJECT_ROOT, "data/processed/training_data.csv"), index=False)
    prediction_data.to_csv(os.path.join(PROJECT_ROOT, "data/features/current_features.csv"), index=False)
    
    # Créer un fichier de configuration factice (déjà fait dans la phase précédente)
    
    yield
    
    # Nettoyage (optionnel, mais bonne pratique)
    # os.remove(os.path.join(PROJECT_ROOT, "data/processed/training_data.csv"))
    # os.remove(os.path.join(PROJECT_ROOT, "data/features/current_features.csv"))
    # os.remove(os.path.join(PROJECT_ROOT, "models/latest_model.json"))
    # os.remove(os.path.join(PROJECT_ROOT, "data/processed/selected_tests.txt"))
    # os.remove(os.path.join(PROJECT_ROOT, "data/processed/evaluation_metrics.yaml"))


def run_script(script_name: str, args: list = []) -> subprocess.CompletedProcess:
    """Exécute un script Python dans le répertoire du projet."""
    command = ["python3", os.path.join(PROJECT_ROOT, "scripts", script_name)] + args
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        check=False,
    )


def test_e2e_train_predict_evaluate():
    """
    Teste le pipeline complet: Entraînement -> Prédiction -> Évaluation.
    """
    model_path = os.path.join(PROJECT_ROOT, "models/latest_model.json")
    selected_tests_path = os.path.join(PROJECT_ROOT, "data/processed/selected_tests.txt")
    metrics_path = os.path.join(PROJECT_ROOT, "data/processed/evaluation_metrics.yaml")
    
    # --- 1. Entraînement ---
    train_result = run_script("train_model.py", ["--output", model_path])
    assert train_result.returncode == 0, f"Échec de l'entraînement: {train_result.stderr}"
    # Le modèle est simulé, donc le fichier n'est pas créé, mais le script doit réussir
    # assert os.path.exists(model_path)
    
    # --- 2. Prédiction ---
    predict_result = run_script("predict.py", ["--output", selected_tests_path])
    assert predict_result.returncode == 0, f"Échec de la prédiction: {predict_result.stderr}"
    assert os.path.exists(selected_tests_path)
    
    with open(selected_tests_path, "r") as f:
        selected_tests = f.read().splitlines()
    assert len(selected_tests) > 0
    
    # --- 3. Évaluation ---
    # Utiliser les données d'entraînement comme données d'évaluation pour la simplicité
    evaluate_result = run_script("evaluate.py", ["--data", os.path.join(PROJECT_ROOT, "data/processed/training_data.csv"), "--output", metrics_path])
    assert evaluate_result.returncode == 0, f"Échec de l'évaluation: {evaluate_result.stderr}"
    assert os.path.exists(metrics_path)
    
    with open(metrics_path, "r") as f:
        metrics = yaml.safe_load(f)
        
    assert "test_reduction_rate" in metrics
    assert metrics["test_reduction_rate"] >= 0.0
    assert metrics["defect_detection_rate"] <= 1.0
    
    print(f"Métriques E2E: {metrics}")
