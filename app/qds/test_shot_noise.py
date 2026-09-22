import numpy as np

from app.qds.states import plus_state
from app.qds.noise import apply_noise_per_shot
from app.qds.measurement import x_basis_probabilities


rng = np.random.default_rng(42)

state = plus_state()

shots = 1000
noise_probability = 0.05

noisy_states = apply_noise_per_shot(
    state=state,
    noise="PHASE_FLIP",
    probability=noise_probability,
    shots=shots,
    rng=rng,
)

plus_count = 0
minus_count = 0

for noisy_state in noisy_states:

    probabilities = x_basis_probabilities(
        noisy_state
    )

    if probabilities["+"] == 1.0:
        plus_count += 1

    elif probabilities["-"] == 1.0:
        minus_count += 1


print("\n===== Q-SENTRY SHOT-LEVEL NOISE TEST =====")

print("\nTotal shots:", shots)

print(
    "Noise probability:",
    noise_probability,
)

print(
    "Expected noisy shots:",
    shots * noise_probability,
)

print(
    "Observed + states:",
    plus_count,
)

print(
    "Observed - states:",
    minus_count,
)

print(
    "Observed noise percentage:",
    (minus_count / shots) * 100,
)