import numpy as np

from app.qds.states import validate_state
from app.qds.entanglement import bell_state


# Single-qubit gates
H = np.array(
    [
        [1 / np.sqrt(2), 1 / np.sqrt(2)],
        [1 / np.sqrt(2), -1 / np.sqrt(2)],
    ],
    dtype=complex,
)

X = np.array(
    [
        [0, 1],
        [1, 0],
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


def kron(*matrices: np.ndarray) -> np.ndarray:
    """
    Compute the Kronecker product of multiple matrices/vectors.
    """
    result = np.array([[1.0]], dtype=complex)

    for matrix in matrices:
        result = np.kron(result, matrix)

    return result


def cnot_three_qubit(control: int, target: int) -> np.ndarray:
    """
    Build a 3-qubit CNOT matrix.

    Qubits are indexed:
        0 = first qubit
        1 = second qubit
        2 = third qubit

    The computational basis ordering is:
        |000>, |001>, |010>, |011>,
        |100>, |101>, |110>, |111>
    """

    matrix = np.zeros((8, 8), dtype=complex)

    for basis_index in range(8):
        bits = [
            (basis_index >> 2) & 1,
            (basis_index >> 1) & 1,
            basis_index & 1,
        ]

        output_bits = bits.copy()

        if bits[control] == 1:
            output_bits[target] ^= 1

        output_index = (
            (output_bits[0] << 2)
            | (output_bits[1] << 1)
            | output_bits[2]
        )

        matrix[output_index, basis_index] = 1.0

    return matrix


def apply_single_qubit_gate(
    state: np.ndarray,
    gate: np.ndarray,
    qubit: int,
) -> np.ndarray:
    """
    Apply a single-qubit gate to one qubit of a 3-qubit state.
    """
    state = np.asarray(state, dtype=complex).reshape(8, 1)

    identity = np.eye(2, dtype=complex)

    operators = []

    for index in range(3):
        operators.append(gate if index == qubit else identity)

    full_gate = kron(*operators)

    return full_gate @ state


def apply_cnot(
    state: np.ndarray,
    control: int,
    target: int,
) -> np.ndarray:
    """
    Apply a CNOT gate to a 3-qubit state.
    """
    gate = cnot_three_qubit(control, target)
    return gate @ state


def measurement_probabilities(state: np.ndarray) -> dict[str, float]:
    """
    Calculate the probabilities of the four possible
    measurement outcomes for the first two qubits.

    Outcomes:
        00
        01
        10
        11
    """

    state = np.asarray(state, dtype=complex).reshape(8, 1)

    probabilities: dict[str, float] = {}

    for outcome in ["00", "01", "10", "11"]:
        probability = 0.0

        q0 = int(outcome[0])
        q1 = int(outcome[1])

        for q2 in [0, 1]:
            index = (q0 << 2) | (q1 << 1) | q2
            probability += abs(state[index, 0]) ** 2

        probabilities[outcome] = float(probability)

    return probabilities


def collapse_and_extract_receiver(
    state: np.ndarray,
    outcome: str,
) -> np.ndarray:
    """
    Collapse the first two qubits to the measured outcome
    and extract the remaining receiver qubit.
    """

    state = np.asarray(state, dtype=complex).reshape(8, 1)

    q0 = int(outcome[0])
    q1 = int(outcome[1])

    receiver = np.zeros((2, 1), dtype=complex)

    for q2 in [0, 1]:
        index = (q0 << 2) | (q1 << 1) | q2
        receiver[q2, 0] = state[index, 0]

    probability = np.linalg.norm(receiver) ** 2

    if np.isclose(probability, 0):
        raise ValueError("Cannot collapse onto an outcome with zero probability.")

    receiver = receiver / np.sqrt(probability)

    return receiver


def apply_pauli_correction(
    receiver: np.ndarray,
    measurement_bits: str,
) -> np.ndarray:
    """
    Apply the standard teleportation correction to the receiver.

    Measurement:
        first bit  -> Z correction
        second bit -> X correction

    Correction:
        X^(second bit) Z^(first bit)
    """

    first_bit = int(measurement_bits[0])
    second_bit = int(measurement_bits[1])

    corrected = receiver.copy()

    if first_bit == 1:
        corrected = Z @ corrected

    if second_bit == 1:
        corrected = X @ corrected

    return corrected


def teleport(
    input_state: np.ndarray,
    rng: np.random.Generator | None = None,
) -> dict:
    """
    Perform one complete quantum teleportation experiment.

    Steps:
        1. Prepare input state.
        2. Prepare Bell pair.
        3. Entangle input and Bell pair.
        4. Perform Bell-basis transformation.
        5. Measure first two qubits.
        6. Collapse receiver qubit.
        7. Apply Pauli correction.
        8. Return the recovered state.
    """

    input_state = validate_state(input_state)

    if rng is None:
        rng = np.random.default_rng()

    # 1. Prepare three-qubit state:
    #    input qubit + Bell pair
    initial_state = kron(input_state, bell_state())

    # 2. Entangle input qubit with Alice's Bell-pair qubit
    state = apply_cnot(initial_state, control=0, target=1)

    # 3. Apply Hadamard to the input qubit
    state = apply_single_qubit_gate(state, H, qubit=0)

    # 4. Calculate measurement probabilities
    measurement_probs = measurement_probabilities(state)

    outcomes = list(measurement_probs.keys())
    probabilities = list(measurement_probs.values())

    # Numerical cleanup
    probabilities = np.array(probabilities, dtype=float)
    probabilities = probabilities / probabilities.sum()

    # 5. Measure first two qubits
    measurement = rng.choice(outcomes, p=probabilities)

    # 6. Collapse and extract Bob's qubit
    receiver_before_correction = collapse_and_extract_receiver(
        state,
        measurement,
    )

    # 7. Apply Pauli correction
    receiver_after_correction = apply_pauli_correction(
        receiver_before_correction,
        measurement,
    )

    return {
        "measurement": measurement,
        "measurement_probabilities": measurement_probs,
        "receiver_before_correction": receiver_before_correction,
        "receiver_after_correction": receiver_after_correction,
    }