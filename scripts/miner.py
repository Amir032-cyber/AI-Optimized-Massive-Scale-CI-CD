import argparse
import os
import sys
from typing import List, Dict, Any

import pandas as pd
from loguru import logger
from git import Repo, Commit, GitCommandError

from pts.utils.logger import setup_logging

# Configuration de la journalisation
setup_logging()
logger.disable("pts")
logger = logger.bind(name="git_miner")


class GitMiner:
    """
    Classe pour l'extraction de données à partir d'un dépôt Git.
    """

    def __init__(self, repo_path: str = ".") -> None:
        """
        Initialise le mineur Git.

        Args:
            repo_path: Chemin vers le dépôt Git local.
        """
        try:
            self.repo = Repo(repo_path)
            logger.info(f"Dépôt Git chargé depuis: {self.repo.working_dir}")
        except GitCommandError as e:
            logger.error(f"Erreur de commande Git: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement du dépôt Git: {e}")
            raise

    def _extract_commit_data(self, commit: Commit) -> Dict[str, Any]:
        """
        Extrait les données pertinentes d'un objet Commit.
        """
        try:
            # Calcul du churn (lignes ajoutées + supprimées)
            churn = commit.stats.total["insertions"] + commit.stats.total["deletions"]

            return {
                "commit_hash": commit.hexsha,
                "author_name": commit.author.name,
                "author_email": commit.author.email,
                "committed_date": commit.committed_date,
                "message": commit.message.strip(),
                "insertions": commit.stats.total["insertions"],
                "deletions": commit.stats.total["deletions"],
                "files_changed": commit.stats.total["files"],
                "churn": churn,
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données du commit {commit.hexsha}: {e}")
            return {}

    def mine_history(self, max_commits: int = 1000) -> pd.DataFrame:
        """
        Mine l'historique du dépôt Git.

        Args:
            max_commits: Nombre maximum de commits à extraire.

        Returns:
            DataFrame contenant l'historique des commits.
        """
        logger.info(f"Démarrage de l'extraction des {max_commits} derniers commits...")
        commit_data: List[Dict[str, Any]] = []
        count = 0

        for commit in self.repo.iter_commits(max_count=max_commits):
            data = self._extract_commit_data(commit)
            if data:
                commit_data.append(data)
                count += 1
            if count >= max_commits:
                break

        df = pd.DataFrame(commit_data)
        logger.info(f"Extraction terminée. {len(df)} commits extraits.")
        return df


def main() -> None:
    """
    Point d'entrée principal pour le script de minage.
    """
    parser = argparse.ArgumentParser(
        description="Outil d'extraction de données à partir d'un dépôt Git."
    )
    parser.add_argument(
        "--repo_path",
        type=str,
        default=".",
        help="Chemin vers le dépôt Git local (par défaut: répertoire courant).",
    )
    parser.add_argument(
        "--max_commits",
        type=int,
        default=1000,
        help="Nombre maximum de commits à extraire (par défaut: 1000).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/commit_history.csv",
        help="Chemin du fichier de sortie CSV.",
    )
    args = parser.parse_args()

    try:
        miner = GitMiner(repo_path=args.repo_path)
        history_df = miner.mine_history(max_commits=args.max_commits)

        # Sauvegarde du résultat
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        history_df.to_csv(args.output, index=False)
        logger.success(f"Historique des commits sauvegardé dans: {args.output}")

    except Exception as e:
        logger.error(f"Échec de l'exécution du mineur Git: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Nécessite l'installation de GitPython: pip install GitPython
    # Pour l'environnement de l'agent, on suppose que le dépôt est déjà cloné.
    main()
