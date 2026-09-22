import numpy as np


def validate_distribution(
    distribution: dict[str, float],
) -> dict[str, float]:
    """
    Validate and normalize a probability distribution.
    """

    if not distribution:
        raise ValueError("Distribution cannot be empty.")

    values = np.array(list(distribution.values()), dtype=float)

    if np.any(values < 0):
        raise ValueError("Probabilities cannot be negative.")

    total = values.sum()

    if np.isclose(total, 0):
        raise ValueError("Distribution cannot sum to zero.")

    return {
        key: float(value / total)
        for key, value in distribution.items()
    }


def absolute_deviations(
    expected: dict[str, float],
    observed: dict[str, float],
) -> dict[str, float]:
    """
    Calculate the absolute probability deviation for each outcome.
    """

    expected = validate_distribution(expected)
    observed = validate_distribution(observed)

    outcomes = set(expected) | set(observed)

    return {
        outcome: abs(
            expected.get(outcome, 0.0)
            - observed.get(outcome, 0.0)
        )
        for outcome in outcomes
    }


def total_variation_distance(
    expected: dict[str, float],
    observed: dict[str, float],
) -> float:
    """
    Calculate total variation distance between two
    probability distributions.

    TVD = 1/2 * sum(|P(x) - Q(x)|)
    """

    deviations = absolute_deviations(expected, observed)

    return float(0.5 * sum(deviations.values()))


def maximum_deviation(
    expected: dict[str, float],
    observed: dict[str, float],
) -> float:
    """
    Return the largest absolute probability deviation
    among all outcomes.
    """

    deviations = absolute_deviations(expected, observed)

    return float(max(deviations.values()))


def compare_distributions(
    expected: dict[str, float],
    observed: dict[str, float],
) -> dict[str, object]:
    """
    Produce a compact statistical comparison between
    expected and observed distributions.
    """

    deviations = absolute_deviations(expected, observed)

    return {
        "expected": validate_distribution(expected),
        "observed": validate_distribution(observed),
        "absolute_deviations": deviations,
        "total_variation_distance": total_variation_distance(
            expected,
            observed,
        ),
        "maximum_deviation": maximum_deviation(
            expected,
            observed,
        ),
    }