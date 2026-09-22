import numpy as np

from app.qds.qds_protocol import run_qds_protocol
from app.qds.attack_experiment import run_noisy_measurement_experiment
from app.qds.detector import evaluate_deviation


def run_noise_robustness_experiment(
    message_bit: int,
    basis: str = "X",
    shots: int = 1000,
    noise: str = "PHASE_FLIP",
    noise_levels: list[float] | None = None,
    threshold: float = 0.03,
    seed: int | None = 42,
) -> dict[str, object]:
    """
    Evaluate detector behaviour across multiple
    simulated noise levels.

    Example noise levels:

        0%
        1%
        2%
        5%
        10%
        20%

    For each noise level:

        Legitimate QDS state
                ↓
        Independent noise per shot
                ↓
        Measurement
                ↓
        Observed distribution
                ↓
        TVD
                ↓
        Threshold decision

    IMPORTANT:
    This experiment measures prototype behaviour.
    It does not establish a universal security threshold.
    """

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    if shots <= 0:
        raise ValueError(
            "shots must be greater than 0."
        )

    if threshold < 0:
        raise ValueError(
            "threshold must be non-negative."
        )

    basis = basis.upper()

    if basis not in ("X", "Y", "Z"):
        raise ValueError(
            "basis must be 'X', 'Y', or 'Z'."
        )

    noise = noise.upper()

    if noise not in (
        "BIT_FLIP",
        "PHASE_FLIP",
        "DEPOLARIZING",
    ):
        raise ValueError(
            "noise must be 'BIT_FLIP', "
            "'PHASE_FLIP', or 'DEPOLARIZING'."
        )

    if noise_levels is None:
        noise_levels = [
            0.00,
            0.01,
            0.02,
            0.05,
            0.10,
            0.20,
        ]

    for level in noise_levels:

        if not 0.0 <= level <= 1.0:
            raise ValueError(
                "Every noise level must be between 0 and 1."
            )

    # ---------------------------------------------------------
    # Random generator
    # ---------------------------------------------------------

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # Generate legitimate baseline state
    # ---------------------------------------------------------

    normal_result = run_qds_protocol(
        message_bit=message_bit,
        basis=basis,
        shots=shots,
        attack=None,
        rng=rng,
    )

    expected = normal_result[
        "expected_probabilities"
    ]

    state = normal_result[
        "receiver_state"
    ]

    # ---------------------------------------------------------
    # Run each noise level
    # ---------------------------------------------------------

    results = []

    for level in noise_levels:

        noisy_result = run_noisy_measurement_experiment(
            state=state,
            basis=basis,
            shots=shots,
            noise=noise,
            noise_probability=level,
            rng=rng,
        )

        detection = evaluate_deviation(
            expected=expected,
            observed=noisy_result[
                "observed_probabilities"
            ],
            threshold=threshold,
        )

        results.append(
            {
                "noise_probability": float(level),
                "noise_percentage": float(
                    level * 100
                ),
                "observed_probabilities":
                    noisy_result[
                        "observed_probabilities"
                    ],
                "measurement_counts":
                    noisy_result[
                        "measurement_counts"
                    ],
                "total_variation_distance":
                    detection[
                        "total_variation_distance"
                    ],
                "maximum_deviation":
                    detection[
                        "maximum_deviation"
                    ],
                "status":
                    detection["status"],
            }
        )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    return {
        "experiment": {
            "message_bit": message_bit,
            "basis": basis,
            "shots": shots,
            "noise": noise,
            "threshold": float(threshold),
            "seed": seed,
            "noise_levels": noise_levels,
        },

        "expected_probabilities": expected,

        "results": results,
    }