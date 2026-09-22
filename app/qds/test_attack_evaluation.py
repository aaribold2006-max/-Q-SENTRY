from app.qds.attack_evaluation import run_attack_evaluation


result = run_attack_evaluation(
    message_bit=0,
    basis="X",
    shots=1000,
    threshold=0.058,
    noise_levels=[0.00, 0.01, 0.02, 0.05],
    seed=42,
)


print("\n========================================")
print("        Q-SENTRY ATTACK EVALUATION")
print("========================================")

print("\nConfiguration:")
for key, value in result["configuration"].items():
    print(f"{key}: {value}")


print("\n----------------------------------------")
print("Evaluation Matrix")
print("----------------------------------------")

print(
    f"{'Condition':<12}"
    f"{'Attack':<8}"
    f"{'Noise':<10}"
    f"{'TVD':<10}"
    f"{'Status'}"
)

print("-" * 60)

for item in result["results"]:

    attack = item["attack"] if item["attack"] else "-"

    print(
        f"{item['condition']:<12}"
        f"{attack:<8}"
        f"{item['noise_probability'] * 100:<9.1f}%"
        f"{item['tvd']:<10.3f}"
        f"{item['status']}"
    )


metrics = result["metrics"]

print("\n----------------------------------------")
print("Metrics")
print("----------------------------------------")

print(
    f"Normal Cases       : "
    f"{metrics['total_normal_cases']}"
)

print(
    f"False Rejections   : "
    f"{metrics['false_rejections']}"
)

print(
    f"False Rejection Rate: "
    f"{metrics['false_rejection_rate'] * 100:.2f}%"
)

print(
    f"Attack Cases       : "
    f"{metrics['total_attack_cases']}"
)

print(
    f"Attack Detections  : "
    f"{metrics['attack_detections']}"
)

print(
    f"Attack Detection Rate: "
    f"{metrics['attack_detection_rate'] * 100:.2f}%"
)

print("\n========================================")