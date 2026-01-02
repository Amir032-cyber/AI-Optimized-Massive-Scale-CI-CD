import os
import yaml
from typing import Any, Dict, Optional

from loguru import logger

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="helpers")


def load_yaml_config(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Charge un fichier de configuration YAML.

    Args:
        file_path: Chemin vers le fichier YAML.

    Returns:
        Dictionnaire de configuration ou None en cas d'erreur.
    """
    if not os.path.exists(file_path):
        logger.error(f"Fichier de configuration non trouvé: {file_path}")
        return None

    try:
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration chargée avec succès depuis: {file_path}")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Erreur de parsing YAML dans {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement de {file_path}: {e}")
        return None


def get_project_root() -> str:
    """
    Retourne le chemin absolu vers la racine du projet.
    """
    # Dans cet environnement, la racine est le répertoire courant
    return os.getcwd()


if __name__ == "__main__":
    # Exemple d'utilisation
    # Création d'un fichier de configuration temporaire
    temp_config_path = "temp_config.yaml"
    temp_config_content = """
    app:
      name: PTS
      version: 0.1.0
    database:
      host: localhost
      port: 5432
    """
    with open(temp_config_path, "w") as f:
        f.write(temp_config_content)

    config = load_yaml_config(temp_config_path)
    if config:
        logger.info(f"Nom de l'application: {config['app']['name']}")

    os.remove(temp_config_path)
    
    logger.info(f"Racine du projet: {get_project_root()}")
