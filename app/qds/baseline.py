import numpy as np

from app.qds.experiment import run_distribution_experiment
from app.qds.attack_experiment import run_noisy_measurement_experiment
from app.qds.statistics import (
    validate_distribution,
    total_variation_distance,
)


def generate_baseline(
    expected: dict[str, float],
    shots_per_run: int = 1000,
    runs: int = 20,
    seed: int | None = 42,
    state: np.ndarray | None = None,
    basis: str | None = None,
    noise: str | None = None,
    noise_probability: float = 0.0,
) -> dict[str, object]:
    """
    Generate repeated legitimate baseline experiments.

    Two modes are supported:

    1. Distribution mode
       Uses the existing expected distribution directly.

    2. State + measurement mode
       Uses a legitimate quantum state and performs
       shot-level measurement with optional noise.

    The second mode is used for noise-aware calibration.
    """

    if shots_per_run <= 0:
        raise ValueError(
            "shots_per_run must be greater than 0."
        )

    if runs <= 0:
        raise ValueError(
            "runs must be greater than 0."
        )

    if noise_probability < 0 or noise_probability > 1:
        raise ValueError(
            "noise_probability must be between 0 and 1."
        )

    validate_distribution(expected)

    rng = np.random.default_rng(seed)

    experiments = []
    tvds = []

    # ---------------------------------------------------------
    # MODE 1: Existing distribution baseline
    # ---------------------------------------------------------

    if state is None:

        for _ in range(runs):

            result = run_distribution_experiment(
                expected=expected,
                shots=shots_per_run,
                rng=rng,
            )

            observed = result["observed"]

            tvd = total_variation_distance(
                expected,
                observed,
            )

            result["total_variation_distance"] = float(tvd)

            experiments.append(result)
            tvds.append(tvd)

    # ---------------------------------------------------------
    # MODE 2: Quantum state + shot-level noise baseline
    # ---------------------------------------------------------

    else:

        if basis is None:
            raise ValueError(
                "basis is required when state is provided."
            )

        for _ in range(runs):

            result = run_noisy_measurement_experiment(
                state=state,
                basis=basis,
                shots=shots_per_run,
                noise=noise,
                noise_probability=noise_probability,
                rng=rng,
            )

            observed = result[
                "observed_probabilities"
            ]

            tvd = total_variation_distance(
                expected,
                observed,
            )

            result["total_variation_distance"] = float(tvd)

            experiments.append(result)
            tvds.append(tvd)

    tvds_array = np.asarray(
        tvds,
        dtype=float,
    )

    return {
        "expected": expected,
        "shots_per_run": shots_per_run,
        "runs": runs,
        "seed": seed,
        "noise": noise,
        "noise_probability": float(
            noise_probability
        ),
        "experiments": experiments,
        "tvd_values": tvds,
        "mean_tvd": float(
            np.mean(tvds_array)
        ),
        "std_tvd": float(
            np.std(tvds_array)
        ),
        "max_tvd": float(
            np.max(tvds_array)
        ),
    }