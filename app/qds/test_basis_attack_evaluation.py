from app.qds.attack_experiment import run_attack_experiment


THRESHOLD = 0.058
SHOTS = 1000
NOISE_LEVELS = [0.00, 0.01, 0.02, 0.05]
BASES = ["X", "Y", "Z"]
ATTACKS = ["X", "Z"]


print("\n==============================================")
print(" Q-SENTRY COMPLEMENTARY-BASIS ATTACK TEST")
print("==============================================")

print(
    f"{'Basis':<8}"
    f"{'Attack':<8}"
    f"{'Noise':<9}"
    f"{'TVD':<9}"
    f"{'Status'}"
)

print("-" * 60)

for basis in BASES:

    for attack in ATTACKS:

        for noise_probability in NOISE_LEVELS:

            result = run_attack_experiment(
                message_bit=0,
                basis=basis,
                shots=SHOTS,
                attack=attack,
                threshold=THRESHOLD,
                seed=42,
                noise="PHASE_FLIP",
                noise_probability=noise_probability,
            )

            detection = result["attack_with_noise"]["detection"]

            print(
                f"{basis:<8}"
                f"{attack:<8}"
                f"{noise_probability * 100:<8.1f}%"
                f"{detection['total_variation_distance']:<9.3f}"
                f"{detection['status']}"
            )


print("\n==============================================")
print(" TEST COMPLETE")
print("==============================================")