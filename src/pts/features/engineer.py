from typing import Dict, Any

import pandas as pd
from loguru import logger

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="feature_engineer")


class FeatureEngineer:
    """
    Crée de nouvelles caractéristiques (features) à partir des caractéristiques existantes.
    """

    def __init__(self, config: Dict[str, Any] = {}) -> None:
        """
        Initialise l'ingénieur de caractéristiques.

        Args:
            config: Dictionnaire de configuration.
        """
        self.config = config

    def create_interaction_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée des caractéristiques d'interaction.

        Args:
            features_df: DataFrame des caractéristiques existantes.

        Returns:
            DataFrame avec les nouvelles caractéristiques d'interaction.
        """
        logger.info("Création des caractéristiques d'interaction.")
        
        # Interaction 1: Churn * Taux d'échec historique
        if "churn" in features_df.columns and "historical_failure_rate" in features_df.columns:
            features_df["churn_failure_interaction"] = (
                features_df["churn"] * features_df["historical_failure_rate"]
            )
        
        # Interaction 2: Expérience de l'auteur / Churn (risque de changement par un auteur moins expérimenté)
        if "author_experience" in features_df.columns and "churn" in features_df.columns:
            # Éviter la division par zéro
            features_df["exp_churn_ratio"] = features_df.apply(
                lambda row: row["author_experience"] / row["churn"]
                if row["churn"] > 0
                else row["author_experience"],
                axis=1,
            )
            
        return features_df

    def encode_categorical_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Encode les caractéristiques catégorielles (ex: one-hot encoding).

        Args:
            features_df: DataFrame des caractéristiques.

        Returns:
            DataFrame avec les caractéristiques encodées.
        """
        logger.info("Encodage des caractéristiques catégorielles.")
        
        # Exemple d'encodage pour 'commit_type'
        if "commit_type" in features_df.columns:
            features_df = pd.get_dummies(
                features_df, columns=["commit_type"], prefix="type"
            )
            
        return features_df

    def run_engineering_pipeline(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Exécute le pipeline complet d'ingénierie de caractéristiques.

        Args:
            features_df: DataFrame des caractéristiques extraites.

        Returns:
            DataFrame final prêt pour l'entraînement du modèle.
        """
        features_df = self.create_interaction_features(features_df)
        features_df = self.encode_categorical_features(features_df)
        
        logger.success("Ingénierie de caractéristiques terminée.")
        return features_df


if __name__ == "__main__":
    # Exemple d'utilisation (nécessite des données extraites)
    # Simulation de données extraites
    data = {
        "commit_id": [f"hash_{i % 10}" for i in range(20)],
        "test_id": [f"test_{i % 5}" for i in range(20)],
        "test_failed": [1 if i % 5 == 0 else 0 for i in range(20)],
        "churn": [10, 50, 20, 100, 5] * 4,
        "author_experience": [10, 5, 5, 5, 5] * 4,
        "historical_failure_rate": [0.1, 0.5, 0.2, 0.9, 0.05] * 4,
        "commit_type": ["feature", "fix", "docs", "feature", "fix"] * 4,
    }
    sample_features_df = pd.DataFrame(data)
    
    engineer = FeatureEngineer()
    engineered_df = engineer.run_engineering_pipeline(sample_features_df)
    
    logger.info("Aperçu des caractéristiques ingéniées:")
    print(engineered_df.head())
    
    # Sauvegarde des caractéristiques ingéniées
    import os
    os.makedirs("data/features", exist_ok=True)
    engineered_df.to_csv("data/features/engineered_features.csv", index=False)
    logger.success("Caractéristiques ingéniées sauvegardées.")
