import numpy as np

from app.qds.qds_protocol import (
    run_qds_protocol,
    get_measurement_probabilities,
)

from app.qds.detector import evaluate_deviation

from app.qds.noise import apply_noise_per_shot

from app.qds.measurement import (
    sample_measurements,
    counts_to_probabilities,
)


def run_noisy_measurement_experiment(
    state: np.ndarray,
    basis: str,
    shots: int,
    noise: str | None,
    noise_probability: float,
    rng: np.random.Generator,
) -> dict[str, object]:
    """
    Perform repeated measurements with independently
    sampled noise for every shot.

    Flow:

        Quantum state
             ↓
        Shot 1 → noise → measurement
        Shot 2 → noise → measurement
        ...
        Shot N → noise → measurement
             ↓
        Measurement counts
             ↓
        Observed probabilities
    """

    noisy_states = apply_noise_per_shot(
        state=state,
        noise=noise,
        probability=noise_probability,
        shots=shots,
        rng=rng,
    )

    counts: dict[str, int] = {}

    for noisy_state in noisy_states:

        probabilities = get_measurement_probabilities(
            noisy_state,
            basis,
        )

        measurement = sample_measurements(
            probabilities,
            shots=1,
            rng=rng,
        )

        for outcome, count in measurement.items():

            if outcome not in counts:
                counts[outcome] = 0

            counts[outcome] += count

    observed_probabilities = counts_to_probabilities(
        counts
    )

    return {
        "noise": noise,
        "noise_probability": float(noise_probability),
        "measurement_counts": counts,
        "observed_probabilities": observed_probabilities,
    }


def run_attack_experiment(
    message_bit: int,
    basis: str = "X",
    shots: int = 1000,
    attack: str = "Z",
    threshold: float = 0.03,
    seed: int | None = 42,
    noise: str | None = None,
    noise_probability: float = 0.0,
) -> dict[str, object]:
    """
    Run the Q-SENTRY normal-vs-attack experiment
    with optional shot-level quantum noise.

    Conditions tested:

        1. NORMAL
        2. NORMAL + NOISE
        3. ATTACK
        4. ATTACK + NOISE

    Noise is independently sampled for every
    measurement shot.

    IMPORTANT:
    An anomalous result does not automatically prove
    that an attack occurred.
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

    if attack is None:
        raise ValueError(
            "attack must be 'X' or 'Z'."
        )

    attack = attack.upper()

    if attack not in ("X", "Z"):
        raise ValueError(
            "attack must be 'X' or 'Z'."
        )

    basis = basis.upper()

    if basis not in ("X", "Y", "Z"):
        raise ValueError(
            "basis must be 'X', 'Y', or 'Z'."
        )

    if not 0.0 <= noise_probability <= 1.0:
        raise ValueError(
            "noise_probability must be between 0 and 1."
        )

    if noise is not None:

        noise = noise.upper()

        if noise not in (
            "BIT_FLIP",
            "PHASE_FLIP",
            "DEPOLARIZING",
        ):
            raise ValueError(
                "noise must be None, 'BIT_FLIP', "
                "'PHASE_FLIP', or 'DEPOLARIZING'."
            )

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # 1. NORMAL EXPERIMENT
    # ---------------------------------------------------------

    normal_result = run_qds_protocol(
        message_bit=message_bit,
        basis=basis,
        shots=shots,
        attack=None,
        rng=rng,
    )

    normal_detection = evaluate_deviation(
        expected=normal_result["expected_probabilities"],
        observed=normal_result["observed_probabilities"],
        threshold=threshold,
    )

    # ---------------------------------------------------------
    # 2. NORMAL + NOISE
    # ---------------------------------------------------------

    normal_noisy_result = run_noisy_measurement_experiment(
        state=normal_result["receiver_state"],
        basis=basis,
        shots=shots,
        noise=noise,
        noise_probability=noise_probability,
        rng=rng,
    )

    normal_noisy_detection = evaluate_deviation(
        expected=normal_result["expected_probabilities"],
        observed=normal_noisy_result["observed_probabilities"],
        threshold=threshold,
    )

    # ---------------------------------------------------------
    # 3. ATTACK EXPERIMENT
    # ---------------------------------------------------------

    attack_result = run_qds_protocol(
        message_bit=message_bit,
        basis=basis,
        shots=shots,
        attack=attack,
        rng=rng,
    )

    attack_detection = evaluate_deviation(
        expected=attack_result["expected_probabilities"],
        observed=attack_result["observed_probabilities"],
        threshold=threshold,
    )

    # ---------------------------------------------------------
    # 4. ATTACK + NOISE
    # ---------------------------------------------------------

    attack_noisy_result = run_noisy_measurement_experiment(
        state=attack_result["tested_state"],
        basis=basis,
        shots=shots,
        noise=noise,
        noise_probability=noise_probability,
        rng=rng,
    )

    attack_noisy_detection = evaluate_deviation(
        expected=attack_result["expected_probabilities"],
        observed=attack_noisy_result["observed_probabilities"],
        threshold=threshold,
    )

    # ---------------------------------------------------------
    # 5. Return complete experiment
    # ---------------------------------------------------------

    return {
        "experiment": {
            "message_bit": message_bit,
            "basis": basis,
            "shots": shots,
            "attack": attack,
            "threshold": float(threshold),
            "seed": seed,
            "noise": noise,
            "noise_probability": float(
                noise_probability
            ),
        },

        "normal": normal_result,

        "normal_detection": normal_detection,

        "normal_with_noise": {
            **normal_noisy_result,
            "detection": normal_noisy_detection,
        },

        "attack": attack_result,

        "attack_detection": attack_detection,

        "attack_with_noise": {
            **attack_noisy_result,
            "detection": attack_noisy_detection,
        },
    }