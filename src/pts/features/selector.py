from typing import Dict, Any, List

import pandas as pd
from loguru import logger
from sklearn.feature_selection import SelectKBest, f_classif

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="feature_selector")


class FeatureSelector:
    """
    Sélectionne les caractéristiques les plus pertinentes pour l'entraînement du modèle.
    """

    def __init__(self, config: Dict[str, Any] = {}) -> None:
        """
        Initialise le sélecteur de caractéristiques.

        Args:
            config: Dictionnaire de configuration.
        """
        self.config = config
        self.k_best = self.config.get("k_best", 10)
        self.target_column = self.config.get("target_column", "test_failed")
        self.selected_features: List[str] = []

    def select_k_best(self, data_df: pd.DataFrame) -> pd.DataFrame:
        """
        Utilise SelectKBest (ANOVA F-value) pour sélectionner les K meilleures caractéristiques.

        Args:
            data_df: DataFrame contenant les caractéristiques et la colonne cible.

        Returns:
            DataFrame avec uniquement les caractéristiques sélectionnées.
        """
        logger.info(f"Démarrage de la sélection des {self.k_best} meilleures caractéristiques.")

        # Préparation des données
        X = data_df.drop(columns=[self.target_column, "commit_id", "test_id"], errors="ignore")
        y = data_df[self.target_column]
        
        # S'assurer que toutes les colonnes de X sont numériques
        X_numeric = X.select_dtypes(include=['number'])
        
        if X_numeric.empty:
            logger.warning("Aucune caractéristique numérique trouvée pour la sélection. Retourne toutes les colonnes.")
            self.selected_features = X.columns.tolist()
            return data_df

        # Initialisation du sélecteur
        selector = SelectKBest(score_func=f_classif, k=min(self.k_best, X_numeric.shape[1]))
        
        # Entraînement du sélecteur
        selector.fit(X_numeric, y)
        
        # Récupération des noms des caractéristiques sélectionnées
        selected_indices = selector.get_support(indices=True)
        self.selected_features = X_numeric.columns[selected_indices].tolist()
        
        logger.info(f"Caractéristiques sélectionnées: {self.selected_features}")
        
        # Retourner le DataFrame avec les colonnes sélectionnées + les colonnes d'identification
        id_cols = ["commit_id", "test_id", self.target_column]
        final_cols = [col for col in id_cols if col in data_df.columns] + self.selected_features
        
        return data_df[final_cols]

    def run_selection_pipeline(self, engineered_df: pd.DataFrame) -> pd.DataFrame:
        """
        Exécute le pipeline complet de sélection de caractéristiques.

        Args:
            engineered_df: DataFrame des caractéristiques ingéniées.

        Returns:
            DataFrame final prêt pour l'entraînement.
        """
        final_df = self.select_k_best(engineered_df)
        
        logger.success("Sélection de caractéristiques terminée.")
        return final_df


if __name__ == "__main__":
    # Exemple d'utilisation (nécessite des données ingéniées)
    # Simulation de données ingéniées
    data = {
        "commit_id": [f"hash_{i % 10}" for i in range(20)],
        "test_id": [f"test_{i % 5}" for i in range(20)],
        "test_failed": [1 if i % 5 == 0 else 0 for i in range(20)],
        "churn": [10, 50, 20, 100, 5] * 4,
        "author_experience": [10, 5, 5, 5, 5] * 4,
        "historical_failure_rate": [0.1, 0.5, 0.2, 0.9, 0.05] * 4,
        "churn_failure_interaction": [1, 2, 3, 4, 5] * 4,
        "type_feature": [1, 0, 0, 1, 0] * 4,
        "type_fix": [0, 1, 0, 0, 1] * 4,
    }
    sample_engineered_df = pd.DataFrame(data)
    
    config = {"k_best": 5}
    selector = FeatureSelector(config=config)
    selected_df = selector.run_selection_pipeline(sample_engineered_df)
    
    logger.info("Aperçu des données sélectionnées:")
    print(selected_df.head())
    
    # Sauvegarde des données sélectionnées
    import os
    os.makedirs("data/features", exist_ok=True)
    selected_df.to_csv("data/features/selected_features.csv", index=False)
    logger.success("Caractéristiques sélectionnées sauvegardées.")
