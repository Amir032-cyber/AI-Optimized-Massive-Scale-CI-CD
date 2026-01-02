from typing import Dict, Any, List, Optional

from loguru import logger
import requests

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="gitlab_integration")


class GitLabIntegration:
    """
    Classe pour interagir avec l'API GitLab.
    """

    def __init__(self, private_token: str, project_id: int, base_url: str = "https://gitlab.com/api/v4") -> None:
        """
        Initialise l'intégration GitLab.

        Args:
            private_token: Jeton d'accès privé GitLab.
            project_id: ID du projet GitLab.
            base_url: URL de base de l'API GitLab.
        """
        self.base_url = f"{base_url}/projects/{project_id}"
        self.headers = {
            "Private-Token": private_token,
        }
        logger.info(f"Intégration GitLab initialisée pour le projet ID: {project_id}")

    def get_commit_details(self, commit_sha: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'un commit.

        Args:
            commit_sha: Le SHA du commit.

        Returns:
            Dictionnaire des détails du commit ou None en cas d'échec.
        """
        url = f"{self.base_url}/repository/commits/{commit_sha}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "id": data["id"],
                "author_name": data["author_name"],
                "committed_date": data["committed_date"],
                "message": data["message"],
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des détails du commit {commit_sha}: {e}")
            return None

    def get_merge_request_changes(self, mr_iid: int) -> List[str]:
        """
        Récupère la liste des fichiers modifiés dans une Merge Request.

        Args:
            mr_iid: L'Internal ID (IID) de la Merge Request.

        Returns:
            Liste des chemins de fichiers modifiés.
        """
        url = f"{self.base_url}/merge_requests/{mr_iid}/changes"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            changed_files = [change["new_path"] for change in data.get("changes", [])]
            logger.info(f"MR !{mr_iid}: {len(changed_files)} fichiers modifiés trouvés.")
            return changed_files
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des changements de la MR !{mr_iid}: {e}")
            return []


if __name__ == "__main__":
    # Exemple d'utilisation (simulé)
    logger.info("Exemple d'utilisation de GitLabIntegration simulé.")
    pass
