from typing import Dict, Any

import pandas as pd
from loguru import logger
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator
from xgboost import XGBClassifier

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="trainer")


class ModelTrainer:
    """
    Gère l'entraînement et la sauvegarde du modèle de sélection prédictive des tests.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialise l'entraîneur de modèle.

        Args:
            config: Dictionnaire de configuration pour l'entraînement du modèle.
        """
        self.config = config
        self.model: Optional[BaseEstimator] = None
        self.model_params = self.config.get("model_params", {})
        self.target_column = self.config.get("target_column", "test_failed")

    def train(self, data_df: pd.DataFrame) -> BaseEstimator:
        """
        Entraîne le modèle sur les données fournies.

        Args:
            data_df: DataFrame contenant les caractéristiques et la colonne cible.

        Returns:
            Le modèle entraîné.
        """
        logger.info(f"Démarrage de l'entraînement du modèle avec {len(data_df)} échantillons.")

        # Préparation des données
        if self.target_column not in data_df.columns:
            logger.error(f"Colonne cible '{self.target_column}' non trouvée dans les données.")
            raise ValueError(f"Colonne cible manquante: {self.target_column}")

        X = data_df.drop(columns=[self.target_column, "test_id"], errors="ignore")
        y = data_df[self.target_column]

        # Séparation des données (simple pour l'exemple)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Initialisation du modèle (XGBoost par défaut)
        model_type = self.config.get("model_type", "XGBClassifier")
        if model_type == "XGBClassifier":
            self.model = XGBClassifier(
                use_label_encoder=False, eval_metric="logloss", **self.model_params
            )
        else:
            logger.warning(f"Type de modèle '{model_type}' non supporté. Utilisation de XGBClassifier.")
            self.model = XGBClassifier(
                use_label_encoder=False, eval_metric="logloss", **self.model_params
            )

        # Entraînement
        self.model.fit(X_train, y_train)
        logger.success("Modèle entraîné avec succès.")

        # Évaluation rapide (pour information)
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        logger.info(f"Score d'entraînement (Accuracy): {train_score:.4f}")
        logger.info(f"Score de test (Accuracy): {test_score:.4f}")

        return self.model

    def save_model(self, path: str) -> None:
        """
        Sauvegarde le modèle entraîné.

        Args:
            path: Chemin du fichier de sauvegarde.
        """
        if self.model is None:
            logger.warning("Aucun modèle à sauvegarder.")
            return

        # Exemple de sauvegarde pour XGBoost
        try:
            # self.model.save_model(path)
            logger.info(f"Modèle sauvegardé (simulé) dans: {path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du modèle: {e}")


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

    config_example = {
        "model_type": "XGBClassifier",
        "target_column": "test_failed",
        "model_params": {"n_estimators": 100, "max_depth": 3},
    }

    trainer = ModelTrainer(config=config_example)
    trained_model = trainer.train(sample_data_df)
    trainer.save_model("models/test_model.json")
