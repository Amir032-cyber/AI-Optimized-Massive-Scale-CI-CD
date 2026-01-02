import argparse
import sys
import os
import pandas as pd
import yaml
from loguru import logger

from pts.core.predictor import PredictiveTestSelector
from pts.utils.logger import setup_logging
from pts.utils.helpers import load_yaml_config

setup_logging()
logger.disable("pts")
logger = logger.bind(name="predict_script")


def main() -> None:
    """Point d'entrée principal pour la prédiction des tests."""
    parser = argparse.ArgumentParser(
        description="Script de prédiction des tests pertinents à exécuter."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/model_config.yaml",
        help="Chemin vers le fichier de configuration du modèle.",
    )
    parser.add_argument(
        "--features",
        type=str,
        default="data/features/current_features.csv",
        help="Chemin vers le fichier de caractéristiques (features) à utiliser pour la prédiction.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/selected_tests.txt",
        help="Chemin du fichier de sortie pour la liste des tests sélectionnés.",
    )
    args = parser.parse_args()

    # 1. Charger la configuration
    config = load_yaml_config(args.config)
    if not config:
        sys.exit(1)

    # 2. Charger les caractéristiques
    try:
        features_df = pd.read_csv(args.features)
        logger.info(f"Caractéristiques chargées depuis {args.features}. {len(features_df)} lignes.")
    except FileNotFoundError:
        logger.error(f"Fichier de caractéristiques non trouvé: {args.features}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des caractéristiques: {e}")
        sys.exit(1)

    # 3. Initialiser le sélecteur
    selection_threshold = config.get("selection_threshold", 0.6)
    model_path = config.get("model_save_path", "models/latest_model.json")
    
    # NOTE: Dans un cas réel, le modèle serait chargé ici.
    # Pour la démo, on utilise le chargement simulé du Predictor.
    selector = PredictiveTestSelector(threshold=selection_threshold, model_path=model_path)

    # 4. Exécuter la prédiction
    try:
        selected_tests = selector.run_prediction_pipeline(features_df)
        
        # 5. Sauvegarder les résultats
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(args.output, "w") as f:
            f.write("\n".join(selected_tests))
            
        logger.success(f"Prédiction terminée. {len(selected_tests)} tests sélectionnés et sauvegardés dans {args.output}")
        
    except Exception as e:
        logger.error(f"Échec du pipeline de prédiction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
