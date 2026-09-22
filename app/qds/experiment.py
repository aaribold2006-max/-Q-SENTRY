import numpy as np

from app.qds.measurement import (
    sample_measurements,
    counts_to_probabilities,
)
from app.qds.statistics import compare_distributions


def run_distribution_experiment(
    expected: dict[str, float],
    shots: int = 1000,
    rng: np.random.Generator | None = None,
) -> dict[str, object]:
    """
    Run a complete measurement experiment.

    Flow:
        Expected probabilities
            ↓
        Repeated measurements
            ↓
        Measurement counts
            ↓
        Empirical probabilities
            ↓
        Statistical comparison
    """

    if rng is None:
        rng = np.random.default_rng()

    # 1. Generate measurement outcomes.
    counts = sample_measurements(
        expected,
        shots=shots,
        rng=rng,
    )

    # 2. Convert counts into observed probabilities.
    observed = counts_to_probabilities(counts)

    # 3. Compare expected vs observed behaviour.
    comparison = compare_distributions(
        expected,
        observed,
    )

    return {
        "shots": shots,
        "expected": comparison["expected"],
        "counts": counts,
        "observed": comparison["observed"],
        "absolute_deviations": comparison["absolute_deviations"],
        "total_variation_distance": comparison["total_variation_distance"],
        "maximum_deviation": comparison["maximum_deviation"],
    }