from typing import Dict, Any, Tuple

import pandas as pd
from loguru import logger
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.base import BaseEstimator

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="evaluator")


class ModelEvaluator:
    """
    Gère l'évaluation des performances du modèle de sélection prédictive des tests.
    """

    def __init__(self, target_column: str = "test_failed") -> None:
        """
        Initialise l'évaluateur.

        Args:
            target_column: Nom de la colonne cible dans les données.
        """
        self.target_column = target_column

    def evaluate(
        self, model: BaseEstimator, data_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Évalue le modèle sur un jeu de données.

        Args:
            model: Le modèle entraîné à évaluer.
            data_df: DataFrame contenant les caractéristiques et la colonne cible.

        Returns:
            Dictionnaire des métriques d'évaluation.
        """
        logger.info(f"Démarrage de l'évaluation du modèle sur {len(data_df)} échantillons.")

        if self.target_column not in data_df.columns:
            logger.error(f"Colonne cible '{self.target_column}' non trouvée dans les données.")
            return {}

        X = data_df.drop(columns=[self.target_column, "test_id"], errors="ignore")
        y_true = data_df[self.target_column]

        try:
            # Prédictions
            y_pred = model.predict(X)
            y_proba = model.predict_proba(X)[:, 1]

            # Calcul des métriques
            metrics = {
                "accuracy": accuracy_score(y_true, y_pred),
                "precision": precision_score(y_true, y_pred),
                "recall": recall_score(y_true, y_pred),
                "f1_score": f1_score(y_true, y_pred),
                "roc_auc": roc_auc_score(y_true, y_proba),
            }

            logger.info("Résultats de l'évaluation:")
            for metric, value in metrics.items():
                logger.info(f"  {metric.capitalize()}: {value:.4f}")

            return metrics

        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation du modèle: {e}")
            return {}

    def calculate_pts_metrics(
        self,
        prediction_results: pd.DataFrame,
        actual_failures: pd.DataFrame,
        selection_threshold: float,
    ) -> Dict[str, float]:
        """
        Calcule les métriques spécifiques à la sélection prédictive des tests (PTS).

        Args:
            prediction_results: DataFrame avec 'test_id' et 'failure_probability'.
            actual_failures: DataFrame avec 'test_id' et 'test_failed' (vrai/faux).
            selection_threshold: Seuil de probabilité utilisé pour la sélection.

        Returns:
            Dictionnaire des métriques PTS.
        """
        # Fusionner les résultats de prédiction et les échecs réels
        merged_df = pd.merge(
            prediction_results, actual_failures, on="test_id", how="inner"
        )

        # Identifier les tests sélectionnés
        merged_df["selected"] = (
            merged_df["failure_probability"] >= selection_threshold
        ).astype(int)

        # Métriques clés
        total_tests = len(merged_df)
        total_failed = merged_df["test_failed"].sum()
        total_selected = merged_df["selected"].sum()

        # 1. Taux de réduction des tests (Test Reduction Rate - TRR)
        trr = 1.0 - (total_selected / total_tests) if total_tests > 0 else 0.0

        # 2. Taux de détection des défauts (Defect Detection Rate - DDR)
        # Nombre de tests échoués qui ont été sélectionnés
        detected_failures = merged_df[
            (merged_df["test_failed"] == 1) & (merged_df["selected"] == 1)
        ]["test_failed"].sum()
        ddr = detected_failures / total_failed if total_failed > 0 else 1.0

        # 3. Taux de faux positifs (False Positive Rate - FPR)
        # Tests sélectionnés qui n'ont pas échoué (sélection inutile)
        false_positives = merged_df[
            (merged_df["test_failed"] == 0) & (merged_df["selected"] == 1)
        ]["selected"].sum()
        fpr = false_positives / total_selected if total_selected > 0 else 0.0

        pts_metrics = {
            "total_tests": total_tests,
            "total_failed": total_failed,
            "total_selected": total_selected,
            "detected_failures": detected_failures,
            "test_reduction_rate": trr,
            "defect_detection_rate": ddr,
            "false_positive_rate": fpr,
        }

        logger.info("Métriques PTS calculées:")
        logger.info(f"  Test Reduction Rate (TRR): {trr:.4f}")
        logger.info(f"  Defect Detection Rate (DDR): {ddr:.4f}")
        logger.info(f"  False Positive Rate (FPR): {fpr:.4f}")

        return pts_metrics


if __name__ == "__main__":
    # Exemple d'utilisation
    # Création de données simulées
    data = {
        "test_id": [f"test_{i}" for i in range(100)],
        "feature_churn": [float(i % 10) for i in range(100)],
        "feature_history": [float(i % 5) for i in range(100)],
        "test_failed": [1 if i % 10 == 0 else 0 for i in range(100)],
    }
    sample_data_df = pd.DataFrame(data)

    # Simulation d'un modèle entraîné (pour l'évaluation)
    from pts.core.trainer import ModelTrainer

    config_example = {
        "model_type": "XGBClassifier",
        "target_column": "test_failed",
        "model_params": {"n_estimators": 10, "max_depth": 2},
    }
    trainer = ModelTrainer(config=config_example)
    model = trainer.train(sample_data_df)

    # 1. Évaluation classique
    evaluator = ModelEvaluator()
    evaluator.evaluate(model, sample_data_df)

    # 2. Évaluation PTS
    from pts.core.predictor import PredictiveTestSelector

    predictor = PredictiveTestSelector(model=model, threshold=0.5)
    prediction_results = predictor.predict(
        sample_data_df.drop(columns=["test_failed"])
    )

    actual_failures = sample_data_df[["test_id", "test_failed"]]
    pts_metrics = evaluator.calculate_pts_metrics(
        prediction_results, actual_failures, selection_threshold=0.5
    )
