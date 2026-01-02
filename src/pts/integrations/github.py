from typing import Dict, Any, List, Optional

from loguru import logger
import requests

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="github_integration")


class GitHubIntegration:
    """
    Classe pour interagir avec l'API GitHub.
    """

    def __init__(self, token: str, repo_owner: str, repo_name: str) -> None:
        """
        Initialise l'intégration GitHub.

        Args:
            token: Jeton d'accès personnel GitHub.
            repo_owner: Propriétaire du dépôt.
            repo_name: Nom du dépôt.
        """
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        logger.info(f"Intégration GitHub initialisée pour {repo_owner}/{repo_name}")

    def get_commit_details(self, commit_sha: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'un commit, y compris les fichiers modifiés.

        Args:
            commit_sha: Le SHA du commit.

        Returns:
            Dictionnaire des détails du commit ou None en cas d'échec.
        """
        url = f"{self.base_url}/commits/{commit_sha}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extraction des noms de fichiers modifiés
            changed_files = [file["filename"] for file in data.get("files", [])]
            
            return {
                "sha": data["sha"],
                "author": data["commit"]["author"]["name"],
                "date": data["commit"]["author"]["date"],
                "message": data["commit"]["message"],
                "changed_files": changed_files,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des détails du commit {commit_sha}: {e}")
            return None

    def get_pull_request_files(self, pr_number: int) -> List[str]:
        """
        Récupère la liste des fichiers modifiés dans une Pull Request.

        Args:
            pr_number: Le numéro de la Pull Request.

        Returns:
            Liste des chemins de fichiers modifiés.
        """
        url = f"{self.base_url}/pulls/{pr_number}/files"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            changed_files = [file["filename"] for file in data]
            logger.info(f"PR #{pr_number}: {len(changed_files)} fichiers modifiés trouvés.")
            return changed_files
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des fichiers de la PR #{pr_number}: {e}")
            return []


if __name__ == "__main__":
    # Exemple d'utilisation (nécessite un jeton et un dépôt réel)
    # L'exécution est simulée pour éviter d'exposer le jeton
    logger.info("Exemple d'utilisation de GitHubIntegration simulé.")
    # integration = GitHubIntegration(
    #     token="YOUR_TOKEN",
    #     repo_owner="Amir032-cyber",
    #     repo_name="AI-Optimized-Massive-Scale-CI-CD"
    # )
    # commit_details = integration.get_commit_details("HEAD")
    # if commit_details:
    #     logger.info(f"Détails du commit: {commit_details}")
    pass
