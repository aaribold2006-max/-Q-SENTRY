from app.qds.attack_experiment import run_attack_experiment


result = run_attack_experiment(
    message_bit=0,
    basis="X",
    shots=1000,
    attack="Z",
    threshold=0.03,
    seed=42,
    noise="PHASE_FLIP",
    noise_probability=0.05,
)


print("\n===== Q-SENTRY INTEGRATED NOISE EXPERIMENT =====")

print("\nExperiment:")
print(result["experiment"])


print("\n--- NORMAL ---")

print(
    "Observed:",
    result["normal"]["observed_probabilities"],
)

print(
    "TVD:",
    result["normal_detection"][
        "total_variation_distance"
    ],
)

print(
    "Detection:",
    result["normal_detection"]["status"],
)


print("\n--- NORMAL + 5% NOISE ---")

print(
    "Observed:",
    result["normal_with_noise"][
        "observed_probabilities"
    ],
)

print(
    "TVD:",
    result["normal_with_noise"]["detection"][
        "total_variation_distance"
    ],
)

print(
    "Detection:",
    result["normal_with_noise"]["detection"][
        "status"
    ],
)


print("\n--- Z ATTACK ---")

print(
    "Observed:",
    result["attack"]["observed_probabilities"],
)

print(
    "TVD:",
    result["attack_detection"][
        "total_variation_distance"
    ],
)

print(
    "Detection:",
    result["attack_detection"]["status"],
)


print("\n--- Z ATTACK + 5% NOISE ---")

print(
    "Observed:",
    result["attack_with_noise"][
        "observed_probabilities"
    ],
)

print(
    "TVD:",
    result["attack_with_noise"]["detection"][
        "total_variation_distance"
    ],
)

print(
    "Detection:",
    result["attack_with_noise"]["detection"][
        "status"
    ],
)