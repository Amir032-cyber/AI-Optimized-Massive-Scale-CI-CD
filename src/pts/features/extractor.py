from typing import Dict, Any

import pandas as pd
from loguru import logger

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="feature_extractor")


class FeatureExtractor:
    """
    Extrait les caractéristiques brutes à partir des données de commits et de tests.
    """

    def __init__(self, config: Dict[str, Any] = {}) -> None:
        """
        Initialise l'extracteur de caractéristiques.

        Args:
            config: Dictionnaire de configuration.
        """
        self.config = config

    def extract_commit_features(self, commit_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrait les caractéristiques liées aux commits.

        Args:
            commit_df: DataFrame des commits traités.

        Returns:
            DataFrame avec les caractéristiques de commits.
        """
        logger.info("Extraction des caractéristiques de commits.")
        
        # Caractéristique 1: Taux de Churn (déjà calculé dans le processeur, mais on le garde ici pour la clarté)
        # Caractéristique 2: Expérience de l'auteur (déjà calculée)
        
        # Caractéristique 3: Type de commit (simplifié à partir du message)
        def get_commit_type(message: str) -> str:
            if message.startswith("feat"):
                return "feature"
            elif message.startswith("fix"):
                return "fix"
            elif message.startswith("refactor"):
                return "refactor"
            elif message.startswith("test"):
                return "test"
            else:
                return "other"

        commit_df["commit_type"] = commit_df["message"].apply(get_commit_type)
        
        # Caractéristique 4: Taille du commit (nombre de fichiers modifiés)
        # commit_df["commit_size"] = commit_df["files_changed"]
        
        return commit_df

    def extract_test_features(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrait les caractéristiques liées aux tests eux-mêmes.

        Args:
            merged_df: DataFrame fusionné (commits + résultats de tests).

        Returns:
            DataFrame avec les caractéristiques de tests.
        """
        logger.info("Extraction des caractéristiques de tests.")
        
        # Caractéristique 1: Fréquence d'échec historique du test (simplifié)
        # Calculer la moyenne d'échec pour chaque test_id
        test_failure_rate = merged_df.groupby("test_id")["test_failed"].mean().reset_index()
        test_failure_rate.rename(
            columns={"test_failed": "historical_failure_rate"}, inplace=True
        )
        
        # Fusionner avec le DataFrame principal
        merged_df = pd.merge(
            merged_df, test_failure_rate, on="test_id", how="left"
        )
        
        # Caractéristique 2: Ancienneté du test (non implémenté ici, nécessiterait plus de données)
        
        return merged_df

    def run_extraction_pipeline(self, processed_df: pd.DataFrame) -> pd.DataFrame:
        """
        Exécute le pipeline complet d'extraction de caractéristiques.

        Args:
            processed_df: DataFrame des données traitées.

        Returns:
            DataFrame avec toutes les caractéristiques extraites.
        """
        # Les caractéristiques de commits sont déjà en grande partie dans processed_df
        # On ajoute ici les caractéristiques spécifiques aux tests
        features_df = self.extract_test_features(processed_df)
        
        logger.success("Extraction de caractéristiques terminée.")
        return features_df


if __name__ == "__main__":
    # Exemple d'utilisation (nécessite des données traitées)
    # Simulation de données traitées
    data = {
        "commit_id": [f"hash_{i % 10}" for i in range(20)],
        "test_id": [f"test_{i % 5}" for i in range(20)],
        "test_failed": [1 if i % 5 == 0 else 0 for i in range(20)],
        "churn": [10, 50, 20, 100, 5] * 4,
        "author_experience": [10, 5, 5, 5, 5] * 4,
        "message": ["feat: a", "fix: b", "docs: c", "feat: d", "fix: e"] * 4,
    }
    sample_processed_df = pd.DataFrame(data)
    
    extractor = FeatureExtractor()
    features_df = extractor.run_extraction_pipeline(sample_processed_df)
    
    logger.info("Aperçu des caractéristiques extraites:")
    print(features_df.head())
    
    # Sauvegarde des caractéristiques
    import os
    os.makedirs("data/features", exist_ok=True)
    features_df.to_csv("data/features/extracted_features.csv", index=False)
    logger.success("Caractéristiques extraites sauvegardées.")
