from app.qds.attack_experiment import run_attack_experiment


def run_attack_evaluation(
    message_bit: int = 0,
    basis: str = "X",
    shots: int = 1000,
    threshold: float = 0.058,
    noise_levels: list[float] | None = None,
    seed: int = 42,
) -> dict[str, object]:
    """
    Evaluate Q-SENTRY against defined attacks
    under multiple phase-flip noise levels.

    Conditions:

        NORMAL
        X ATTACK
        Z ATTACK

    Noise levels:

        0%, 1%, 2%, 5%

    The function records the measured TVD and
    detector decision for every condition.
    """

    if noise_levels is None:
        noise_levels = [
            0.00,
            0.01,
            0.02,
            0.05,
        ]

    results = []

    # ---------------------------------------------------------
    # Normal conditions
    # ---------------------------------------------------------

    for noise_probability in noise_levels:

        result = run_attack_experiment(
            message_bit=message_bit,
            basis=basis,
            shots=shots,
            attack="Z",
            threshold=threshold,
            seed=seed,
            noise="PHASE_FLIP",
            noise_probability=noise_probability,
        )

        normal_detection = (
            result["normal_with_noise"]["detection"]
        )

        results.append(
            {
                "condition": "NORMAL",
                "attack": None,
                "noise_probability": noise_probability,
                "tvd": normal_detection[
                    "total_variation_distance"
                ],
                "status": normal_detection[
                    "status"
                ],
            }
        )

    # ---------------------------------------------------------
    # Attack conditions
    # ---------------------------------------------------------

    for attack in ("X", "Z"):

        for noise_probability in noise_levels:

            result = run_attack_experiment(
                message_bit=message_bit,
                basis=basis,
                shots=shots,
                attack=attack,
                threshold=threshold,
                seed=seed,
                noise="PHASE_FLIP",
                noise_probability=noise_probability,
            )

            attack_detection = (
                result["attack_with_noise"]["detection"]
            )

            results.append(
                {
                    "condition": "ATTACK",
                    "attack": attack,
                    "noise_probability": noise_probability,
                    "tvd": attack_detection[
                        "total_variation_distance"
                    ],
                    "status": attack_detection[
                        "status"
                    ],
                }
            )

    # ---------------------------------------------------------
    # Summary metrics
    # ---------------------------------------------------------

    normal_results = [
        r for r in results
        if r["condition"] == "NORMAL"
    ]

    attack_results = [
        r for r in results
        if r["condition"] == "ATTACK"
    ]

    false_rejections = sum(
        1
        for r in normal_results
        if r["status"] == "ANOMALOUS"
    )

    attack_detections = sum(
        1
        for r in attack_results
        if r["status"] == "ANOMALOUS"
    )

    return {
        "configuration": {
            "message_bit": message_bit,
            "basis": basis,
            "shots": shots,
            "threshold": threshold,
            "noise": "PHASE_FLIP",
            "noise_levels": noise_levels,
            "seed": seed,
        },

        "results": results,

        "metrics": {
            "total_normal_cases": len(
                normal_results
            ),
            "false_rejections": false_rejections,

            "total_attack_cases": len(
                attack_results
            ),
            "attack_detections": attack_detections,

            "false_rejection_rate": (
                false_rejections
                / len(normal_results)
                if normal_results
                else 0.0
            ),

            "attack_detection_rate": (
                attack_detections
                / len(attack_results)
                if attack_results
                else 0.0
            ),
        },
    }