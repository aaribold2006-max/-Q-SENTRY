import numpy as np


# Computational basis states
ZERO = np.array([[1.0], [0.0]], dtype=complex)
ONE = np.array([[0.0], [1.0]], dtype=complex)


def normalize(state: np.ndarray) -> np.ndarray:
    """
    Normalize a quantum state vector.

    A valid quantum state must have total probability 1.
    """
    state = np.asarray(state, dtype=complex)

    norm = np.linalg.norm(state)

    if np.isclose(norm, 0):
        raise ValueError("A zero vector cannot represent a quantum state.")

    return state / norm


def validate_state(state: np.ndarray) -> np.ndarray:
    """
    Validate and return a normalized single-qubit state.

    Expected shape:
        (2, 1)

    Example:
        [[a],
         [b]]
    where |a|^2 + |b|^2 = 1.
    """
    state = np.asarray(state, dtype=complex)

    if state.shape == (2,):
        state = state.reshape(2, 1)

    if state.shape != (2, 1):
        raise ValueError(
            f"Single-qubit state must have shape (2, 1), got {state.shape}"
        )

    return normalize(state)


def probabilities(state: np.ndarray) -> dict[str, float]:
    """
    Return measurement probabilities in the computational basis.

    For:
        a|0> + b|1>

    returns:
        {
            "0": |a|^2,
            "1": |b|^2
        }
    """
    state = validate_state(state)

    return {
        "0": float(abs(state[0, 0]) ** 2),
        "1": float(abs(state[1, 0]) ** 2),
    }
    
def plus_state() -> np.ndarray:
    """
    Return the |+> state:

        |+> = (|0> + |1>) / sqrt(2)

    When measured in the computational basis,
    the result should be:
        0 -> 50%
        1 -> 50%
    """
    state = (ZERO + ONE) / np.sqrt(2)
    return normalize(state)