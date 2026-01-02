from typing import List, Dict, Any

import pandas as pd
from loguru import logger

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="data_validator")


class DataValidator:
    """
    Gère la validation de la qualité et de la cohérence des données.
    """

    def __init__(self, required_columns: List[str]) -> None:
        """
        Initialise le validateur de données.

        Args:
            required_columns: Liste des colonnes essentielles que le DataFrame doit contenir.
        """
        self.required_columns = required_columns

    def check_missing_values(self, df: pd.DataFrame) -> bool:
        """
        Vérifie la présence de valeurs manquantes dans les colonnes requises.

        Args:
            df: DataFrame à vérifier.

        Returns:
            True si aucune valeur manquante n'est trouvée, False sinon.
        """
        missing_counts = df[self.required_columns].isnull().sum()
        
        if missing_counts.sum() > 0:
            logger.warning(f"Valeurs manquantes détectées dans les colonnes requises:\n{missing_counts[missing_counts > 0]}")
            return False
        
        logger.info("Aucune valeur manquante détectée dans les colonnes requises.")
        return True

    def check_data_types(self, df: pd.DataFrame, expected_types: Dict[str, Any]) -> bool:
        """
        Vérifie si les types de données correspondent aux attentes.

        Args:
            df: DataFrame à vérifier.
            expected_types: Dictionnaire {colonne: type_attendu}.

        Returns:
            True si tous les types correspondent, False sinon.
        """
        type_mismatches = []
        for col, expected_type in expected_types.items():
            if col in df.columns and not pd.api.types.is_dtype_equal(df[col].dtype, expected_type):
                type_mismatches.append(
                    f"Colonne '{col}': Attendu {expected_type}, Trouvé {df[col].dtype}"
                )

        if type_mismatches:
            mismatches_str = "\n".join(type_mismatches)
            logger.warning(f"Incohérences de types de données détectées:\n{mismatches_str}")
            return False
        
        logger.info("Types de données vérifiés et cohérents.")
        return True

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Exécute le pipeline complet de validation.

        Args:
            df: DataFrame à valider.

        Returns:
            True si la validation réussit, False sinon.
        """
        logger.info("Démarrage de la validation des données.")
        
        # 1. Vérification des colonnes requises
        if not all(col in df.columns for col in self.required_columns):
            missing = [col for col in self.required_columns if col not in df.columns]
            logger.error(f"Colonnes requises manquantes: {missing}")
            return False

        # 2. Vérification des valeurs manquantes
        if not self.check_missing_values(df):
            return False

        # 3. Vérification des types de données (exemple)
        expected_types = {
            "commit_id": object,
            "test_id": object,
            "test_failed": int,
            "churn": float,
        }
        if not self.check_data_types(df, expected_types):
            # Peut être une erreur non bloquante si la conversion est possible
            pass 

        logger.success("Validation des données réussie.")
        return True


if __name__ == "__main__":
    # Exemple d'utilisation
    required = ["commit_id", "test_id", "test_failed", "churn"]
    validator = DataValidator(required_columns=required)

    # Données valides
    valid_data = pd.DataFrame({
        "commit_id": ["a", "b"],
        "test_id": ["t1", "t2"],
        "test_failed": [0, 1],
        "churn": [10.0, 20.0],
        "extra_col": [1, 2]
    })
    validator.validate(valid_data)

    # Données invalides (manque une colonne)
    invalid_data_col = pd.DataFrame({
        "commit_id": ["a", "b"],
        "test_id": ["t1", "t2"],
        "test_failed": [0, 1],
    })
    validator.validate(invalid_data_col)

    # Données invalides (valeurs manquantes)
    invalid_data_missing = pd.DataFrame({
        "commit_id": ["a", None],
        "test_id": ["t1", "t2"],
        "test_failed": [0, 1],
        "churn": [10.0, 20.0],
    })
    validator.validate(invalid_data_missing)
