import argparse
import os
import sys
import yaml
import pandas as pd
from loguru import logger

from pts.core.trainer import ModelTrainer
from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="train_script")


def load_config(config_path: str) -> dict:
    """Charge le fichier de configuration YAML."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration chargée depuis: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Fichier de configuration non trouvé: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Erreur de parsing YAML: {e}")
        sys.exit(1)


def load_data(data_path: str) -> pd.DataFrame:
    """Charge les données d'entraînement."""
    try:
        df = pd.read_csv(data_path)
        logger.info(f"Données chargées depuis {data_path}. {len(df)} lignes.")
        return df
    except FileNotFoundError:
        logger.error(f"Fichier de données non trouvé: {data_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {e}")
        sys.exit(1)


def main() -> None:
    """Point d'entrée principal pour l'entraînement du modèle."""
    parser = argparse.ArgumentParser(
        description="Script d'entraînement du modèle de sélection prédictive des tests."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/model_config.yaml",
        help="Chemin vers le fichier de configuration du modèle.",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/processed/training_data.csv",
        help="Chemin vers le fichier de données d'entraînement.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/latest_model.json",
        help="Chemin pour sauvegarder le modèle entraîné.",
    )
    args = parser.parse_args()

    # 1. Charger la configuration
    config = load_config(args.config)

    # 2. Charger les données (Simulation: Création de données factices si le fichier n'existe pas)
    try:
        data_df = load_data(args.data)
    except SystemExit:
        logger.warning(f"Fichier de données non trouvé à {args.data}. Création de données factices pour la démonstration.")
        data = {
            "test_id": [f"test_{i}" for i in range(100)],
            "feature_churn": [float(i % 10) for i in range(100)],
            "feature_history": [float(i % 5) for i in range(100)],
            "test_failed": [1 if i % 10 == 0 else 0 for i in range(100)],
        }
        data_df = pd.DataFrame(data)

    # 3. Entraîner le modèle
    trainer = ModelTrainer(config=config)
    try:
        trainer.train(data_df)
        # 4. Sauvegarder le modèle
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        trainer.save_model(args.output)
        logger.success(f"Pipeline d'entraînement terminé. Modèle sauvegardé dans {args.output}")
    except Exception as e:
        logger.error(f"Échec du pipeline d'entraînement: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
