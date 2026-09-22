from app.qds.noise_robustness import (
    run_noise_robustness_experiment,
)


result = run_noise_robustness_experiment(
    message_bit=0,
    basis="X",
    shots=1000,
    noise="PHASE_FLIP",
    noise_levels=[
        0.00,
        0.01,
        0.02,
        0.05,
        0.10,
        0.20,
    ],
    threshold=0.03,
    seed=42,
)


print(
    "\n===== Q-SENTRY NOISE ROBUSTNESS EXPERIMENT ====="
)

print("\nExperiment:")
print(result["experiment"])

print("\nExpected distribution:")
print(result["expected_probabilities"])

print("\n--- RESULTS ---")

for row in result["results"]:

    print(
        f"\nNoise: "
        f"{row['noise_percentage']:.1f}%"
    )

    print(
        "Observed:",
        row["observed_probabilities"],
    )

    print(
        "TVD:",
        row["total_variation_distance"],
    )

    print(
        "Maximum deviation:",
        row["maximum_deviation"],
    )

    print(
        "Detection:",
        row["status"],
    )