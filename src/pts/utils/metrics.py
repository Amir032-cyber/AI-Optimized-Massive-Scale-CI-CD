from typing import Dict, Any

from loguru import logger
from prometheus_client import Gauge, Counter, Histogram, generate_latest

from pts.utils.logger import setup_logging

setup_logging()
logger.disable("pts")
logger = logger.bind(name="metrics_util")

# Définition des métriques Prometheus
# 1. Jauge pour le taux de réduction des tests
TEST_REDUCTION_RATE = Gauge(
    "pts_test_reduction_rate",
    "Taux de réduction des tests (Tests sautés / Total tests)",
)

# 2. Compteur pour les économies de coûts
COST_SAVINGS_USD = Counter(
    "pts_cost_savings_usd_total",
    "Total des économies de coûts réalisées grâce à PTS (en USD)",
)

# 3. Histogramme pour la latence de prédiction
PREDICTION_LATENCY = Histogram(
    "pts_prediction_latency_seconds",
    "Latence de la prédiction ML (en secondes)",
    buckets=(0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, float("inf")),
)


def update_test_reduction_rate(total_tests: int, selected_tests: int) -> float:
    """
    Calcule et met à jour la jauge du taux de réduction des tests.

    Args:
        total_tests: Nombre total de tests.
        selected_tests: Nombre de tests sélectionnés pour l'exécution.

    Returns:
        Le taux de réduction des tests.
    """
    if total_tests == 0:
        trr = 0.0
    else:
        trr = 1.0 - (selected_tests / total_tests)

    TEST_REDUCTION_RATE.set(trr)
    logger.info(f"Mise à jour du Taux de Réduction des Tests (TRR): {trr:.4f}")
    return trr


def increment_cost_savings(amount: float) -> None:
    """
    Incrémente le compteur des économies de coûts.

    Args:
        amount: Montant des économies réalisées (en USD).
    """
    COST_SAVINGS_USD.inc(amount)
    logger.info(f"Économies de coûts incrémentées de {amount} USD.")


def observe_prediction_latency(duration: float) -> None:
    """
    Enregistre la durée d'une prédiction dans l'histogramme de latence.

    Args:
        duration: Durée de la prédiction (en secondes).
    """
    PREDICTION_LATENCY.observe(duration)
    logger.info(f"Latence de prédiction observée: {duration:.4f} secondes.")


def get_prometheus_metrics() -> bytes:
    """
    Génère les métriques Prometheus au format texte.

    Returns:
        Les métriques encodées en bytes.
    """
    return generate_latest()


if __name__ == "__main__":
    # Exemple d'utilisation
    update_test_reduction_rate(total_tests=1000, selected_tests=200)
    increment_cost_savings(amount=5.50)
    observe_prediction_latency(duration=0.052)
    
    metrics = get_prometheus_metrics()
    print("\n--- Métriques Prometheus ---")
    print(metrics.decode("utf-8"))
