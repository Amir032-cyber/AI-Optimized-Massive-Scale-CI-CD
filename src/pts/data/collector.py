import os
from typing import Optional, List, Dict, Any

import pandas as pd
from loguru import logger

from pts.utils.logger import setup_logging
from scripts.miner import GitMiner # Réutilisation du GitMiner

setup_logging()
logger.disable("pts")
logger = logger.bind(name="data_collector")


class DataCollector:
    """
    Gère la collecte des données brutes nécessaires à l'entraînement du modèle PTS.
    """

    def __init__(self, repo_path: str = ".") -> None:
        """
        Initialise le collecteur de données.

        Args:
            repo_path: Chemin vers le dépôt Git local.
        """
        self.repo_path = repo_path
        self.miner = GitMiner(repo_path=repo_path)

    def collect_commit_history(self, max_commits: int = 1000) -> pd.DataFrame:
        """
        Collecte l'historique des commits via le GitMiner.

        Args:
            max_commits: Nombre maximum de commits à extraire.

        Returns:
            DataFrame contenant l'historique des commits.
        """
        logger.info("Démarrage de la collecte de l'historique des commits.")
        commit_df = self.miner.mine_history(max_commits=max_commits)
        return commit_df

    def collect_test_results(self, results_dir: str = "data/raw/test_results") -> pd.DataFrame:
        """
        Collecte les résultats des tests (simulés ou réels).

        Dans un environnement réel, cela impliquerait de parser des fichiers XML/JSON
        générés par les outils de CI/CD (ex: JUnit XML).

        Args:
            results_dir: Répertoire contenant les fichiers de résultats de tests.

        Returns:
            DataFrame contenant les résultats des tests (test_id, commit_hash, failed).
        """
        logger.info(f"Collecte des résultats de tests dans {results_dir} (simulée).")
        
        # Simulation de données de résultats de tests
        data = {
            "test_id": [f"test_{i}" for i in range(100)] * 10,
            "commit_hash": [f"hash_{j}" for j in range(10)] * 100,
            "test_failed": [1 if (i + j) % 15 == 0 else 0 for i in range(100) for j in range(10)],
        }
        df = pd.DataFrame(data)
        
        logger.info(f"Collecte terminée. {len(df)} résultats de tests simulés.")
        return df

    def run_collection_pipeline(self) -> Dict[str, pd.DataFrame]:
        """
        Exécute le pipeline complet de collecte de données.

        Returns:
            Dictionnaire des DataFrames collectés.
        """
        commit_history = self.collect_commit_history(max_commits=50) # Limité pour la démo
        test_results = self.collect_test_results()
        
        return {
            "commit_history": commit_history,
            "test_results": test_results,
        }


if __name__ == "__main__":
    # Exemple d'utilisation
    # Assurez-vous d'être dans un répertoire Git
    try:
        collector = DataCollector(repo_path=os.getcwd())
        collected_data = collector.run_collection_pipeline()
        
        # Sauvegarde des données brutes
        os.makedirs("data/raw", exist_ok=True)
        collected_data["commit_history"].to_csv("data/raw/commit_history.csv", index=False)
        collected_data["test_results"].to_csv("data/raw/test_results.csv", index=False)
        
        logger.success("Données brutes collectées et sauvegardées.")
    except Exception as e:
        logger.error(f"Échec de la collecte de données: {e}")
