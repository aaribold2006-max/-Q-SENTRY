import numpy as np


def validate_single_qubit_state(state: np.ndarray) -> np.ndarray:
    """
    Validate and normalize a single-qubit state.
    """

    state = np.asarray(state, dtype=complex)

    if state.shape == (2,):
        state = state.reshape(2, 1)

    if state.shape != (2, 1):
        raise ValueError(
            f"Single-qubit state must have shape (2, 1), got {state.shape}"
        )

    norm = np.linalg.norm(state)

    if np.isclose(norm, 0):
        raise ValueError("A zero vector cannot represent a quantum state.")

    return state / norm


def z_basis_probabilities(state: np.ndarray) -> dict[str, float]:
    """
    Calculate measurement probabilities in the computational
    (Z) basis.

    |0> -> outcome "0"
    |1> -> outcome "1"
    """

    state = validate_single_qubit_state(state)

    probability_0 = float(abs(state[0, 0]) ** 2)
    probability_1 = float(abs(state[1, 0]) ** 2)

    return {
        "0": probability_0,
        "1": probability_1,
    }
    
def x_basis_probabilities(state: np.ndarray) -> dict[str, float]:
    """
    Calculate measurement probabilities in the X basis.

    X-basis states:
        |+> = (|0> + |1>) / sqrt(2)
        |-> = (|0> - |1>) / sqrt(2)

    The probabilities are obtained by transforming the state
    into the X measurement basis.
    """

    state = validate_single_qubit_state(state)

    plus_amplitude = (
        state[0, 0] + state[1, 0]
    ) / np.sqrt(2)

    minus_amplitude = (
        state[0, 0] - state[1, 0]
    ) / np.sqrt(2)

    probability_plus = float(abs(plus_amplitude) ** 2)
    probability_minus = float(abs(minus_amplitude) ** 2)

    return {
        "+": probability_plus,
        "-": probability_minus,
    }


def y_basis_probabilities(state: np.ndarray) -> dict[str, float]:
    """
    Calculate measurement probabilities in the Y basis.

    Y-basis states:
        |+i> = (|0> + i|1>) / sqrt(2)
        |-i> = (|0> - i|1>) / sqrt(2)

    The probabilities are obtained by transforming the state
    into the Y measurement basis.
    """

    state = validate_single_qubit_state(state)

    plus_i_amplitude = (
        state[0, 0] - 1j * state[1, 0]
    ) / np.sqrt(2)

    minus_i_amplitude = (
        state[0, 0] + 1j * state[1, 0]
    ) / np.sqrt(2)

    probability_plus_i = float(abs(plus_i_amplitude) ** 2)
    probability_minus_i = float(abs(minus_i_amplitude) ** 2)

    return {
        "+i": probability_plus_i,
        "-i": probability_minus_i,
    }
    
def sample_measurements(
    probabilities: dict[str, float],
    shots: int,
    rng: np.random.Generator | None = None,
) -> dict[str, int]:
    """
    Run repeated measurements based on the given probabilities.

    Example:
        {"0": 0.8, "1": 0.2}, 1000 shots

    returns approximately:
        {"0": 800, "1": 200}
    """

    if shots <= 0:
        raise ValueError("shots must be greater than 0.")

    if rng is None:
        rng = np.random.default_rng()

    outcomes = list(probabilities.keys())
    values = np.array(list(probabilities.values()), dtype=float)

    if np.any(values < 0):
        raise ValueError("Probabilities cannot be negative.")

    total = values.sum()

    if not np.isclose(total, 1.0):
        values = values / total

    samples = rng.choice(
        outcomes,
        size=shots,
        p=values,
    )

    counts = {outcome: 0 for outcome in outcomes}

    for sample in samples:
        counts[sample] += 1

    return counts


def counts_to_probabilities(counts: dict[str, int]) -> dict[str, float]:
    """
    Convert measurement counts into empirical probabilities.
    """

    total = sum(counts.values())

    if total <= 0:
        raise ValueError("Measurement counts must contain at least one shot.")

    return {
        outcome: count / total
        for outcome, count in counts.items()
    }