import numpy as np

from app.qds.states import ZERO, ONE, plus_state, normalize
from app.qds.teleportation import teleport
from app.qds.measurement import (
    z_basis_probabilities,
    x_basis_probabilities,
    y_basis_probabilities,
    sample_measurements,
    counts_to_probabilities,
)
from app.qds.statistics import compare_distributions
from app.qds.attacks import pauli_channel_attack


def minus_state() -> np.ndarray:
    """Return the X-basis |-> state."""
    return normalize(ZERO - ONE)


def plus_i_state() -> np.ndarray:
    """Return the Y-basis |+i> state."""
    return normalize(ZERO + 1j * ONE)


def minus_i_state() -> np.ndarray:
    """Return the Y-basis |-i> state."""
    return normalize(ZERO - 1j * ONE)


def prepare_signature_state(
    message_bit: int,
    basis: str,
) -> np.ndarray:
    """Prepare a simple prototype QDS quantum state."""

    if message_bit not in (0, 1):
        raise ValueError("message_bit must be 0 or 1.")

    basis = basis.upper()

    if basis == "Z":
        return ZERO.copy() if message_bit == 0 else ONE.copy()

    if basis == "X":
        return plus_state() if message_bit == 0 else minus_state()

    if basis == "Y":
        return plus_i_state() if message_bit == 0 else minus_i_state()

    raise ValueError("basis must be 'X', 'Y', or 'Z'.")


def get_measurement_probabilities(
    state: np.ndarray,
    basis: str,
) -> dict[str, float]:
    """Return measurement probabilities in the selected basis."""

    basis = basis.upper()

    if basis == "Z":
        return z_basis_probabilities(state)

    if basis == "X":
        return x_basis_probabilities(state)

    if basis == "Y":
        return y_basis_probabilities(state)

    raise ValueError("basis must be 'X', 'Y', or 'Z'.")


def apply_attack(
    state: np.ndarray,
    attack: str | None,
) -> np.ndarray:
    """
    Apply a selected attack scenario.

    None -> normal execution
    Z    -> simplified Z-channel disturbance
    X    -> simplified X-channel disturbance
    """

    if attack is None:
        return state

    return pauli_channel_attack(
        state,
        attack=attack,
    )


def run_qds_protocol(
    message_bit: int,
    basis: str = "Z",
    shots: int = 1000,
    attack: str | None = None,
    rng: np.random.Generator | None = None,
) -> dict[str, object]:
    """
    Run the simplified Q-SENTRY QDS prototype.

    Flow:

        Prepare state
        → Teleport
        → Optional attack
        → Measure receiver
        → Collect statistics
        → Compare with legitimate expectation
    """

    if shots <= 0:
        raise ValueError("shots must be greater than 0.")

    if rng is None:
        rng = np.random.default_rng()

    basis = basis.upper()

    # 1. Prepare signature state.
    signature_state = prepare_signature_state(
        message_bit,
        basis,
    )

    # 2. Teleport to receiver.
    teleport_result = teleport(
        signature_state,
        rng=rng,
    )

    receiver_state = teleport_result["receiver_after_correction"]

    # 3. Apply optional attack.
    tested_state = apply_attack(
        receiver_state,
        attack,
    )

    # 4. Expected legitimate behaviour.
    expected_probabilities = get_measurement_probabilities(
        signature_state,
        basis,
    )

    # 5. Probabilities of the tested receiver state.
    tested_probabilities = get_measurement_probabilities(
        tested_state,
        basis,
    )

    # 6. Repeated measurements.
    counts = sample_measurements(
        tested_probabilities,
        shots,
        rng=rng,
    )

    # 7. Convert counts to observed probabilities.
    observed_probabilities = counts_to_probabilities(
        counts
    )

    # 8. Compare observed behaviour with legitimate expectation.
    comparison = compare_distributions(
        expected_probabilities,
        observed_probabilities,
    )

    return {
        "message_bit": message_bit,
        "basis": basis,
        "shots": shots,
        "scenario": "NORMAL" if attack is None else "ATTACK",
        "attack": attack,
        "signature_state": signature_state,
        "receiver_state": receiver_state,
        "tested_state": tested_state,
        "expected_probabilities": expected_probabilities,
        "observed_probabilities": observed_probabilities,
        "measurement_counts": counts,
        "total_variation_distance": comparison[
            "total_variation_distance"
        ],
        "maximum_deviation": comparison[
            "maximum_deviation"
        ],
    }