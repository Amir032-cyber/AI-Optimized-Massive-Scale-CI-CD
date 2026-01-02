from typing import Dict, Any, Optional

from loguru import logger
import requests

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="jenkins_integration")


class JenkinsIntegration:
    """
    Classe pour interagir avec l'API Jenkins.
    """

    def __init__(self, base_url: str, username: str, api_token: str) -> None:
        """
        Initialise l'intégration Jenkins.

        Args:
            base_url: URL de base de l'instance Jenkins.
            username: Nom d'utilisateur Jenkins.
            api_token: Jeton API Jenkins.
        """
        self.base_url = base_url.rstrip("/")
        self.auth = (username, api_token)
        logger.info(f"Intégration Jenkins initialisée pour {self.base_url}")

    def get_job_info(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un job Jenkins.

        Args:
            job_name: Nom du job.

        Returns:
            Dictionnaire des informations du job ou None en cas d'échec.
        """
        url = f"{self.base_url}/job/{job_name}/api/json"
        try:
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des informations du job {job_name}: {e}")
            return None

    def get_build_test_results(self, job_name: str, build_number: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les résultats de tests d'une construction spécifique.

        Args:
            job_name: Nom du job.
            build_number: Numéro de la construction.

        Returns:
            Dictionnaire des résultats de tests ou None en cas d'échec.
        """
        url = f"{self.base_url}/job/{job_name}/{build_number}/testReport/api/json"
        try:
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des résultats de tests pour {job_name}#{build_number}: {e}")
            return None


if __name__ == "__main__":
    # Exemple d'utilisation (simulé)
    logger.info("Exemple d'utilisation de JenkinsIntegration simulé.")
    pass
