from app.qds.attack_experiment import run_attack_experiment


CALIBRATED_THRESHOLD = 0.058


result = run_attack_experiment(
    message_bit=0,
    basis="X",
    shots=1000,
    attack="Z",
    threshold=CALIBRATED_THRESHOLD,
    seed=42,
    noise="PHASE_FLIP",
    noise_probability=0.05,
)


print("\n===== Q-SENTRY THRESHOLD VALIDATION =====")

print("\nExperiment:")
print(result["experiment"])


print("\n--- NORMAL ---")

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
    "TVD:",
    result["normal_with_noise"]["detection"][
        "total_variation_distance"
    ],
)

print(
    "Detection:",
    result["normal_with_noise"]["detection"]["status"],
)


print("\n--- Z ATTACK ---")

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
    "TVD:",
    result["attack_with_noise"]["detection"][
        "total_variation_distance"
    ],
)

print(
    "Detection:",
    result["attack_with_noise"]["detection"]["status"],
)


print("\n--- THRESHOLD ---")

print(
    "Calibrated candidate threshold:",
    CALIBRATED_THRESHOLD,
)