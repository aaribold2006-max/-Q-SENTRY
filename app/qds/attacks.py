import numpy as np

from app.qds.states import validate_state
from app.qds.teleportation import X, Z


def pauli_channel_attack(
    state: np.ndarray,
    attack: str = "Z",
) -> np.ndarray:
    """
    Apply a controlled Pauli disturbance to a quantum state.

    This is a simplified prototype model of quantum-channel
    manipulation.

    Supported attacks:
        X -> bit-flip disturbance
        Z -> phase-flip disturbance
    """

    state = validate_state(state)

    attack = attack.upper()

    if attack == "X":
        attacked_state = X @ state

    elif attack == "Z":
        attacked_state = Z @ state

    else:
        raise ValueError("attack must be 'X' or 'Z'.")

    return validate_state(attacked_state)