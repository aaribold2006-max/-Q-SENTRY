import numpy as np


def calibrate_candidate_threshold(
    baseline: dict[str, object],
    percentile: float = 95.0,
) -> dict[str, float]:
    """
    Calculate an empirical candidate threshold from legitimate
    baseline experiments.

    IMPORTANT:
    This is a calibration aid for the prototype.
    It is NOT a protocol-defined QDS security threshold.
    """

    if not 0 < percentile <= 100:
        raise ValueError("percentile must be between 0 and 100.")

    experiments = baseline.get("experiments")

    if not experiments:
        raise ValueError("Baseline contains no experiments.")

    tvd_values = np.array(
        [
            float(experiment["total_variation_distance"])
            for experiment in experiments
        ],
        dtype=float,
    )

    threshold = float(np.percentile(tvd_values, percentile))

    return {
        "percentile": percentile,
        "candidate_threshold": threshold,
        "mean_tvd": float(np.mean(tvd_values)),
        "std_tvd": float(np.std(tvd_values)),
        "max_tvd": float(np.max(tvd_values)),
    }