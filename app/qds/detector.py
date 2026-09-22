from app.qds.statistics import compare_distributions


def evaluate_deviation(
    expected: dict[str, float],
    observed: dict[str, float],
    threshold: float,
) -> dict[str, object]:
    """
    Compare observed behaviour against expected behaviour.

    This is a generic anomaly evaluator.
    The threshold must be justified by the selected
    QDS protocol or statistical model.

    It does NOT claim that every anomaly is an attack.
    """

    if threshold < 0:
        raise ValueError("threshold must be non-negative.")

    comparison = compare_distributions(
        expected,
        observed,
    )

    tvd = comparison["total_variation_distance"]
    maximum_deviation = comparison["maximum_deviation"]

    if tvd <= threshold:
        status = "WITHIN_EXPECTED_RANGE"
    else:
        status = "ANOMALOUS"

    return {
        "status": status,
        "threshold": float(threshold),
        "total_variation_distance": tvd,
        "maximum_deviation": maximum_deviation,
        "comparison": comparison,
    }