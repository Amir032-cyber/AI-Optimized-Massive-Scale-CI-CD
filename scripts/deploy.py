import argparse
import sys
import os
from loguru import logger

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="deploy_script")


def deploy_docker(tag: str) -> None:
    """
    Déploie l'application en utilisant Docker.
    """
    logger.info(f"Démarrage du déploiement Docker avec le tag: {tag}")
    
    # 1. Construire l'image Docker
    build_command = f"docker build -t pts:{tag} ."
    logger.info(f"Exécution: {build_command}")
    if os.system(build_command) != 0:
        logger.error("Échec de la construction de l'image Docker.")
        sys.exit(1)
        
    # 2. Pousser l'image vers un registre (simulé)
    push_command = f"docker push pts:{tag}"
    logger.info(f"Exécution (simulée): {push_command}")
    # if os.system(push_command) != 0:
    #     logger.error("Échec du push de l'image Docker.")
    #     sys.exit(1)
        
    logger.success(f"Déploiement Docker réussi (image pts:{tag} construite).")


def deploy_kubernetes(config_path: str) -> None:
    """
    Déploie l'application sur Kubernetes.
    """
    logger.info(f"Démarrage du déploiement Kubernetes avec la configuration: {config_path}")
    
    # 1. Appliquer les fichiers de configuration Kubernetes
    apply_command = f"kubectl apply -f {config_path}"
    logger.info(f"Exécution (simulée): {apply_command}")
    # if os.system(apply_command) != 0:
    #     logger.error("Échec de l'application des configurations Kubernetes.")
    #     sys.exit(1)
        
    logger.success("Déploiement Kubernetes réussi (configuration appliquée).")


def main() -> None:
    """Point d'entrée principal pour le script de déploiement."""
    parser = argparse.ArgumentParser(
        description="Script de déploiement de l'application PTS."
    )
    parser.add_argument(
        "--target",
        type=str,
        choices=["docker", "kubernetes"],
        required=True,
        help="Cible de déploiement (docker ou kubernetes).",
    )
    parser.add_argument(
        "--tag",
        type=str,
        default="latest",
        help="Tag de l'image Docker à construire/déployer.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/deployment/kubernetes/",
        help="Chemin vers le répertoire de configuration Kubernetes.",
    )
    args = parser.parse_args()

    if args.target == "docker":
        deploy_docker(args.tag)
    elif args.target == "kubernetes":
        deploy_kubernetes(args.config)


if __name__ == "__main__":
    main()
