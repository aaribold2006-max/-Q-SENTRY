import numpy as np

from app.qds.states import validate_state


# ---------------------------------------------------------
# Pauli gates
# ---------------------------------------------------------

X = np.array(
    [
        [0, 1],
        [1, 0],
    ],
    dtype=complex,
)

Y = np.array(
    [
        [0, -1j],
        [1j, 0],
    ],
    dtype=complex,
)

Z = np.array(
    [
        [1, 0],
        [0, -1],
    ],
    dtype=complex,
)


# ---------------------------------------------------------
# Bit-flip noise
# ---------------------------------------------------------

def apply_bit_flip_noise(
    state: np.ndarray,
    probability: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Apply probabilistic bit-flip noise.

    With probability p:
        X is applied.

    With probability (1-p):
        The state remains unchanged.
    """

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must be between 0 and 1."
        )

    if rng is None:
        rng = np.random.default_rng()

    state = validate_state(state)

    if rng.random() < probability:
        return validate_state(X @ state)

    return state.copy()


# ---------------------------------------------------------
# Phase-flip noise
# ---------------------------------------------------------

def apply_phase_flip_noise(
    state: np.ndarray,
    probability: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Apply probabilistic phase-flip noise.

    With probability p:
        Z is applied.

    With probability (1-p):
        The state remains unchanged.
    """

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must be between 0 and 1."
        )

    if rng is None:
        rng = np.random.default_rng()

    state = validate_state(state)

    if rng.random() < probability:
        return validate_state(Z @ state)

    return state.copy()


# ---------------------------------------------------------
# Depolarizing noise
# ---------------------------------------------------------

def apply_depolarizing_noise(
    state: np.ndarray,
    probability: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Apply simplified probabilistic depolarizing noise.

    With probability p:
        Randomly apply X, Y, or Z.

    With probability (1-p):
        The state remains unchanged.

    This is a simplified prototype model.
    """

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must be between 0 and 1."
        )

    if rng is None:
        rng = np.random.default_rng()

    state = validate_state(state)

    if rng.random() >= probability:
        return state.copy()

    noise_gate = rng.choice(
        [X, Y, Z]
    )

    return validate_state(noise_gate @ state)


# ---------------------------------------------------------
# Unified noise interface
# ---------------------------------------------------------

def apply_noise(
    state: np.ndarray,
    noise: str | None,
    probability: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Apply the selected noise model.

    Supported values:

        None
        BIT_FLIP
        PHASE_FLIP
        DEPOLARIZING
    """

    if rng is None:
        rng = np.random.default_rng()

    if noise is None:
        return validate_state(state)

    noise = noise.upper()

    if noise == "BIT_FLIP":
        return apply_bit_flip_noise(
            state,
            probability,
            rng,
        )

    if noise == "PHASE_FLIP":
        return apply_phase_flip_noise(
            state,
            probability,
            rng,
        )

    if noise == "DEPOLARIZING":
        return apply_depolarizing_noise(
            state,
            probability,
            rng,
        )

    raise ValueError(
        "noise must be None, 'BIT_FLIP', "
        "'PHASE_FLIP', or 'DEPOLARIZING'."
    )


# ---------------------------------------------------------
# Shot-level noise
# ---------------------------------------------------------

def apply_noise_per_shot(
    state: np.ndarray,
    noise: str | None,
    probability: float,
    shots: int,
    rng: np.random.Generator | None = None,
) -> list[np.ndarray]:
    """
    Generate one independently noise-tested state per shot.

    Example:

        shots = 1000
        probability = 0.05

    means every shot independently has a 5% probability
    of receiving the selected noise event.

    This allows Q-SENTRY to model repeated measurements
    under controlled statistical noise.
    """

    if shots <= 0:
        raise ValueError(
            "shots must be greater than 0."
        )

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must be between 0 and 1."
        )

    if rng is None:
        rng = np.random.default_rng()

    states = []

    for _ in range(shots):

        noisy_state = apply_noise(
            state=state,
            noise=noise,
            probability=probability,
            rng=rng,
        )

        states.append(noisy_state)

    return states