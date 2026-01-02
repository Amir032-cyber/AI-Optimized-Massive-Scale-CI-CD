import sys
from loguru import logger
from typing import Optional

def setup_logging(level: str = "INFO", sink: Optional[str] = None) -> None:
    """
    Configure la journalisation (logging) pour l'application PTS.

    Utilise Loguru pour une journalisation simple et efficace.

    Args:
        level: Niveau de journalisation minimum (ex: "INFO", "DEBUG", "WARNING").
        sink: Destination des logs (ex: "sys.stderr", "file.log").
    """
    logger.remove()  # Supprime le gestionnaire par défaut
    
    # Ajoute un nouveau gestionnaire pour la sortie standard (stderr)
    logger.add(
        sink=sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        diagnose=True,
    )

    # Ajoute un gestionnaire pour un fichier si spécifié
    if sink:
        logger.add(
            sink=sink,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            compression="zip",
            enqueue=True,  # Rend la journalisation asynchrone et plus rapide
        )

    logger.info(f"Journalisation configurée au niveau: {level}")

# Exemple d'utilisation (peut être appelé dans le point d'entrée de l'application)
if __name__ == "__main__":
    setup_logging(level="DEBUG", sink="pts_app.log")
    
    # L'utilisation de logger.bind permet d'ajouter un contexte
    app_logger = logger.bind(name="main_app")
    
    app_logger.debug("Ceci est un message de débogage.")
    app_logger.info("L'application démarre.")
    app_logger.warning("Attention: une configuration par défaut est utilisée.")
    try:
        1 / 0
    except ZeroDivisionError:
        app_logger.exception("Une erreur critique s'est produite.")
