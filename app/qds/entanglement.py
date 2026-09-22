import numpy as np


# Bell state:
#
# |Φ+> = (|00> + |11>) / sqrt(2)
#
# A two-qubit state is represented as:
# [ |00>,
#   |01>,
#   |10>,
#   |11> ]

PHI_PLUS = np.array(
    [
        [1 / np.sqrt(2)],
        [0],
        [0],
        [1 / np.sqrt(2)],
    ],
    dtype=complex,
)


def bell_state() -> np.ndarray:
    """
    Return the Bell state |Φ+>.

    |Φ+> = (|00> + |11>) / sqrt(2)
    """
    return PHI_PLUS.copy()


def two_qubit_probabilities(state: np.ndarray) -> dict[str, float]:
    """
    Return computational-basis measurement probabilities
    for a two-qubit state.

    Keys represent:
        00
        01
        10
        11
    """
    state = np.asarray(state, dtype=complex)

    if state.shape == (4,):
        state = state.reshape(4, 1)

    if state.shape != (4, 1):
        raise ValueError(
            f"Two-qubit state must have shape (4, 1), got {state.shape}"
        )

    probabilities = np.abs(state[:, 0]) ** 2

    return {
        "00": float(probabilities[0]),
        "01": float(probabilities[1]),
        "10": float(probabilities[2]),
        "11": float(probabilities[3]),
    }