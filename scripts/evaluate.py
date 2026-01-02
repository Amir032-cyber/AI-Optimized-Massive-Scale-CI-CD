import argparse
import sys
import os
import pandas as pd
import yaml
from loguru import logger

from pts.core.evaluator import ModelEvaluator
from pts.core.predictor import PredictiveTestSelector
from pts.utils.logger import setup_logging
from pts.utils.helpers import load_yaml_config

setup_logging()
logger.disable("pts")
logger = logger.bind(name="evaluate_script")


def main() -> None:
    """Point d'entrée principal pour l'évaluation du modèle."""
    parser = argparse.ArgumentParser(
        description="Script d'évaluation du modèle de sélection prédictive des tests."
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
        default="data/processed/evaluation_data.csv",
        help="Chemin vers le fichier de données d'évaluation (incluant la colonne cible).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/evaluation_metrics.yaml",
        help="Chemin du fichier de sortie pour les métriques d'évaluation.",
    )
    args = parser.parse_args()

    # 1. Charger la configuration
    config = load_yaml_config(args.config)
    if not config:
        sys.exit(1)

    # 2. Charger les données
    try:
        data_df = pd.read_csv(args.data)
        logger.info(f"Données chargées depuis {args.data}. {len(data_df)} lignes.")
    except FileNotFoundError:
        logger.error(f"Fichier de données non trouvé: {args.data}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {e}")
        sys.exit(1)

    # 3. Initialiser le sélecteur et l'évaluateur
    selection_threshold = config.get("selection_threshold", 0.6)
    model_path = config.get("model_save_path", "models/latest_model.json")
    
    # NOTE: Le modèle doit être chargé pour l'évaluation
    # Pour la démo, on utilise le chargement simulé du Predictor.
    selector = PredictiveTestSelector(threshold=selection_threshold, model_path=model_path)
    evaluator = ModelEvaluator(target_column=config.get("target_column", "test_failed"))

    try:
        # 4. Évaluation classique (nécessite un modèle entraîné)
        # model = selector.model # Récupérer le modèle chargé
        # metrics = evaluator.evaluate(model, data_df)
        
        # Simulation des résultats de prédiction pour l'évaluation PTS
        prediction_results = selector.predict(data_df.drop(columns=[evaluator.target_column], errors="ignore"))
        actual_failures = data_df[["test_id", evaluator.target_column]].rename(columns={evaluator.target_column: "test_failed"})
        
        # 5. Évaluation PTS
        pts_metrics = evaluator.calculate_pts_metrics(
            prediction_results, actual_failures, selection_threshold=selection_threshold
        )
        
        # 6. Sauvegarder les métriques
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(args.output, "w") as f:
            yaml.dump(pts_metrics, f, default_flow_style=False)
            
        logger.success(f"Pipeline d'évaluation terminé. Métriques sauvegardées dans {args.output}")
        
    except Exception as e:
        logger.error(f"Échec du pipeline d'évaluation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
