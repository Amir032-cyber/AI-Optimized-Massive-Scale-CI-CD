from typing import Dict, Any

import pandas as pd
from loguru import logger

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="data_processor")


class DataProcessor:
    """
    Gère le nettoyage, la transformation et la fusion des données brutes.
    """

    def __init__(self, config: Dict[str, Any] = {}) -> None:
        """
        Initialise le processeur de données.

        Args:
            config: Dictionnaire de configuration pour le traitement.
        """
        self.config = config

    def clean_and_transform_commits(self, commit_df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et transforme les données d'historique de commits.

        Args:
            commit_df: DataFrame des commits bruts.

        Returns:
            DataFrame des commits transformés.
        """
        logger.info("Nettoyage et transformation des données de commits.")
        
        # Conversion de la date
        commit_df["committed_date"] = pd.to_datetime(commit_df["committed_date"], unit="s")
        
        # Extraction de features simples (ex: jour de la semaine, heure)
        commit_df["day_of_week"] = commit_df["committed_date"].dt.dayofweek
        commit_df["hour_of_day"] = commit_df["committed_date"].dt.hour
        
        # Calcul du score d'expérience de l'auteur (simplifié)
        author_counts = commit_df["author_name"].value_counts()
        commit_df["author_experience"] = commit_df["author_name"].map(author_counts)
        
        # Sélection des colonnes pertinentes
        processed_df = commit_df[
            [
                "commit_hash",
                "author_name",
                "author_experience",
                "churn",
                "files_changed",
                "day_of_week",
                "hour_of_day",
            ]
        ].copy()
        
        logger.info(f"Transformation terminée. {len(processed_df)} lignes.")
        return processed_df

    def merge_data(self, commit_df: pd.DataFrame, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Fusionne les données de commits et les résultats de tests.

        Args:
            commit_df: DataFrame des commits transformés.
            results_df: DataFrame des résultats de tests.

        Returns:
            DataFrame fusionné prêt pour l'ingénierie de caractéristiques.
        """
        logger.info("Fusion des données de commits et des résultats de tests.")
        
        # Renommer la colonne pour la fusion
        commit_df = commit_df.rename(columns={"commit_hash": "commit_id"})
        results_df = results_df.rename(columns={"commit_hash": "commit_id"})
        
        # Fusion sur l'ID du commit
        merged_df = pd.merge(
            results_df, commit_df, on="commit_id", how="left"
        )
        
        # Gestion des valeurs manquantes (commits non trouvés)
        merged_df.dropna(subset=["author_name"], inplace=True)
        
        logger.info(f"Fusion terminée. {len(merged_df)} lignes.")
        return merged_df

    def run_processing_pipeline(self, raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Exécute le pipeline complet de traitement des données.

        Args:
            raw_data: Dictionnaire des DataFrames bruts.

        Returns:
            DataFrame traité.
        """
        commit_df = raw_data["commit_history"]
        results_df = raw_data["test_results"]
        
        processed_commits = self.clean_and_transform_commits(commit_df)
        merged_data = self.merge_data(processed_commits, results_df)
        
        return merged_data


if __name__ == "__main__":
    # Exemple d'utilisation (nécessite des données brutes)
    # Simulation de données brutes
    raw_commits = {
        "commit_hash": [f"hash_{i}" for i in range(10)],
        "author_name": ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice", "Charlie", "Bob", "Alice", "Charlie"],
        "committed_date": [1672531200 + i * 3600 for i in range(10)], # Timestamps
        "churn": [10, 50, 20, 100, 5, 15, 30, 60, 25, 40],
        "files_changed": [2, 5, 1, 8, 1, 3, 2, 6, 4, 3],
        "message": ["feat: a", "fix: b", "docs: c", "feat: d", "fix: e", "refactor: f", "test: g", "chore: h", "feat: i", "fix: j"],
        "insertions": [5, 25, 10, 50, 2, 7, 15, 30, 12, 20],
        "deletions": [5, 25, 10, 50, 3, 8, 15, 30, 13, 20],
    }
    raw_results = {
        "test_id": [f"test_{i}" for i in range(20)],
        "commit_hash": [f"hash_{i % 10}" for i in range(20)],
        "test_failed": [1 if i % 5 == 0 else 0 for i in range(20)],
    }
    
    raw_data = {
        "commit_history": pd.DataFrame(raw_commits),
        "test_results": pd.DataFrame(raw_results),
    }
    
    processor = DataProcessor()
    processed_df = processor.run_processing_pipeline(raw_data)
    
    logger.info("Aperçu des données traitées:")
    print(processed_df.head())
    
    # Sauvegarde des données traitées
    os.makedirs("data/processed", exist_ok=True)
    processed_df.to_csv("data/processed/merged_data.csv", index=False)
    logger.success("Données traitées sauvegardées.")
