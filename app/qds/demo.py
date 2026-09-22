from app.qds.attack_experiment import run_attack_experiment


THRESHOLD = 0.058
SHOTS = 1000
NOISE = "PHASE_FLIP"
NOISE_PROBABILITY = 0.05


def run_demo():

    print("\n==============================================")
    print("              Q-SENTRY DEMO")
    print("==============================================")

    print("\nConfiguration")
    print("----------------------------------------------")
    print("Protocol        : Prototype Teleportation QDS")
    print("Message Bit     : 0")
    print("Measurement     : X basis")
    print("Shots           :", SHOTS)
    print("Noise           :", NOISE)
    print("Noise Level     :", "5%")
    print("Threshold       :", THRESHOLD)

    # -------------------------------------------------
    # RUN EXPERIMENT
    # -------------------------------------------------

    result = run_attack_experiment(
        message_bit=0,
        basis="X",
        shots=SHOTS,
        attack="Z",
        threshold=THRESHOLD,
        seed=42,
        noise=NOISE,
        noise_probability=NOISE_PROBABILITY,
    )

    normal = result["normal_with_noise"]
    attack = result["attack_with_noise"]

    normal_detection = normal["detection"]
    attack_detection = attack["detection"]

    # -------------------------------------------------
    # NORMAL CONDITION
    # -------------------------------------------------

    print("\n==============================================")
    print("              NORMAL CONDITION")
    print("==============================================")

    print(
        "Observed Distribution :",
        normal["observed_probabilities"],
    )

    print(
        "TVD                   :",
        normal_detection["total_variation_distance"],
    )

    print(
        "Security Decision     :",
        normal_detection["status"],
    )

    # -------------------------------------------------
    # ATTACK CONDITION
    # -------------------------------------------------

    print("\n==============================================")
    print("              ATTACK CONDITION")
    print("==============================================")

    print("Attack                : Z Pauli")

    print(
        "Observed Distribution :",
        attack["observed_probabilities"],
    )

    print(
        "TVD                   :",
        attack_detection["total_variation_distance"],
    )

    print(
        "Security Decision     :",
        attack_detection["status"],
    )

    # -------------------------------------------------
    # COMPARISON
    # -------------------------------------------------

    print("\n==============================================")
    print("          SECURITY EVIDENCE COMPARISON")
    print("==============================================")

    print(
        f"{'Metric':<25}"
        f"{'Normal':<15}"
        f"{'Z Attack'}"
    )

    print("-" * 55)

    print(
        f"{'TVD':<25}"
        f"{normal_detection['total_variation_distance']:<15.3f}"
        f"{attack_detection['total_variation_distance']:.3f}"
    )

    print(
        f"{'Threshold':<25}"
        f"{THRESHOLD:<15.3f}"
        f"{THRESHOLD:.3f}"
    )

    print(
        f"{'Decision':<25}"
        f"{normal_detection['status']:<15}"
        f"{attack_detection['status']}"
    )

    # -------------------------------------------------
    # EXPLANATION
    # -------------------------------------------------

    print("\n==============================================")
    print("          EXPLAINABLE SECURITY EVIDENCE")
    print("==============================================")

    print("\n1. Measurement")
    print(
        "   Q-SENTRY collects repeated quantum"
        " measurement outcomes."
    )

    print("\n2. Statistical Analysis")
    print(
        "   The observed distribution is compared"
        " using Total Variation Distance (TVD)."
    )

    print("\n3. Threshold Analysis")
    print(
        f"   Candidate threshold = {THRESHOLD}"
    )

    print("\n4. Security Decision")

    if normal_detection["status"] == "WITHIN_EXPECTED_RANGE":
        print(
            "   Normal behaviour remained within"
            " the calibrated expected range."
        )
    else:
        print(
            "   Normal behaviour exceeded"
            " the calibrated expected range."
        )

    if attack_detection["status"] == "ANOMALOUS":
        print(
            "   The defined Z-Pauli attack produced"
            " anomalous measurement behaviour."
        )
    else:
        print(
            "   The defined attack was not distinguished"
            " under this configuration."
        )

    print("\nImportant limitation:")
    print(
        "   An anomalous result indicates statistical"
        " deviation from expected behaviour."
    )

    print(
        "   It does not automatically prove a specific attack."
    )

    print(
        "   Attack observability depends on the"
        " quantum state and measurement basis."
    )

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------

    print("\n==============================================")
    print("              Q-SENTRY SUMMARY")
    print("==============================================")

    print("Simulation        : COMPLETE")
    print("Measurement       : COMPLETE")
    print("Statistical Test  : TVD")
    print("Threshold         : CALIBRATED CANDIDATE")

    print(
        "Normal Test       :",
        normal_detection["status"],
    )

    print(
        "Attack Test       :",
        attack_detection["status"],
    )

    print("Security Evidence : MEASURABLE")

    print("\n==============================================")
    print("              DEMO COMPLETE")
    print("==============================================")


if __name__ == "__main__":
    run_demo()