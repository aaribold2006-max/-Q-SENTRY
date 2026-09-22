from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.qds.attack_experiment import run_attack_experiment


class SimulationManager:
    """
    Controls Q-SENTRY simulation experiments.

    This manager connects the application layer to the
    existing quantum experiment engine.

    Important:
    The existing run_attack_experiment() function requires
    an attack value and provides:
        - normal_with_noise
        - attack_with_noise

    Therefore:
        NORMAL and NOISE use normal_with_noise
        ATTACK and ATTACK_WITH_NOISE use attack_with_noise
    """

    VALID_SCENARIOS = {
        "NORMAL",
        "NOISE",
        "ATTACK",
        "ATTACK_WITH_NOISE",
    }

    VALID_BASES = {
        "X",
        "Y",
        "Z",
    }

    VALID_ATTACKS = {
        "X",
        "Z",
    }

    VALID_NOISE = {
        "PHASE_FLIP",
        "BIT_FLIP",
        "DEPOLARIZING",
    }

    def __init__(self) -> None:
        self.last_result: dict[str, Any] | None = None

    def run(
        self,
        scenario: str = "NORMAL",
        message_bit: int = 0,
        basis: str = "X",
        shots: int = 1000,
        attack: str = "Z",
        threshold: float = 0.058,
        seed: int = 42,
        noise: str = "PHASE_FLIP",
        noise_probability: float = 0.0,
        protocol_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run a controlled Q-SENTRY simulation.
        """

        scenario = scenario.strip().upper()
        basis = basis.strip().upper()
        attack = attack.strip().upper()
        noise = noise.strip().upper()

        self._validate_inputs(
            scenario=scenario,
            message_bit=message_bit,
            basis=basis,
            shots=shots,
            attack=attack,
            threshold=threshold,
            noise=noise,
            noise_probability=noise_probability,
        )

        experiment_result = run_attack_experiment(
            message_bit=message_bit,
            basis=basis,
            shots=shots,
            attack=attack,
            threshold=threshold,
            seed=seed,
            noise=noise,
            noise_probability=noise_probability,
        )

        # ---------------------------------------------------------------
        # Select the correct result from the existing experiment engine.
        # ---------------------------------------------------------------

        if scenario == "NORMAL":
            selected_result = experiment_result[
                "normal_with_noise"
            ]

        elif scenario == "NOISE":
            selected_result = experiment_result[
                "normal_with_noise"
            ]

        elif scenario == "ATTACK":
            selected_result = experiment_result[
                "attack_with_noise"
            ]

        elif scenario == "ATTACK_WITH_NOISE":
            selected_result = experiment_result[
                "attack_with_noise"
            ]

        else:
            raise ValueError(
                f"Unsupported simulation scenario: {scenario}"
            )

        simulation_result = {
            "simulation": {
                "scenario": scenario,
                "protocol_id": protocol_id,
                "message_bit": message_bit,
                "basis": basis,
                "shots": shots,
                "attack": attack,
                "noise": noise,
                "noise_probability": float(
                    noise_probability
                ),
                "threshold": float(threshold),
                "seed": seed,
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },

            "result": selected_result,

            "comparison": {
                "normal_result": experiment_result.get(
                    "normal_with_noise"
                ),
                "attack_with_noise_result": (
                    experiment_result.get(
                        "attack_with_noise"
                    )
                ),
            },
        }

        self.last_result = simulation_result

        return simulation_result

    def run_normal(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Run a normal-condition simulation.
        """
        return self.run(
            scenario="NORMAL",
            **kwargs,
        )

    def run_noise_test(
        self,
        noise: str = "PHASE_FLIP",
        noise_probability: float = 0.05,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Run a normal-condition simulation with controlled noise.
        """
        return self.run(
            scenario="NOISE",
            noise=noise,
            noise_probability=noise_probability,
            **kwargs,
        )

    def run_attack_test(
        self,
        attack: str = "Z",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Run a defined attack simulation.

        Noise can be set to 0 to represent the
        attack-only condition.
        """
        return self.run(
            scenario="ATTACK",
            attack=attack,
            noise_probability=0.0,
            **kwargs,
        )

    def run_attack_noise_test(
        self,
        attack: str = "Z",
        noise: str = "PHASE_FLIP",
        noise_probability: float = 0.05,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Run an attack under controlled noise.
        """
        return self.run(
            scenario="ATTACK_WITH_NOISE",
            attack=attack,
            noise=noise,
            noise_probability=noise_probability,
            **kwargs,
        )

    def get_last_result(
        self,
    ) -> dict[str, Any] | None:
        """
        Return the most recent simulation result.
        """
        return self.last_result

    def _validate_inputs(
        self,
        scenario: str,
        message_bit: int,
        basis: str,
        shots: int,
        attack: str,
        threshold: float,
        noise: str,
        noise_probability: float,
    ) -> None:
        """
        Validate simulation inputs.
        """

        if scenario not in self.VALID_SCENARIOS:
            raise ValueError(
                "scenario must be one of: "
                + ", ".join(
                    sorted(self.VALID_SCENARIOS)
                )
            )

        if message_bit not in {0, 1}:
            raise ValueError(
                "message_bit must be 0 or 1."
            )

        if basis not in self.VALID_BASES:
            raise ValueError(
                "basis must be X, Y, or Z."
            )

        if shots <= 0:
            raise ValueError(
                "shots must be greater than 0."
            )

        if attack not in self.VALID_ATTACKS:
            raise ValueError(
                "attack must be X or Z."
            )

        if threshold < 0 or threshold > 1:
            raise ValueError(
                "threshold must be between 0 and 1."
            )

        if noise not in self.VALID_NOISE:
            raise ValueError(
                "noise must be PHASE_FLIP, "
                "BIT_FLIP, or DEPOLARIZING."
            )

        if noise_probability < 0 or noise_probability > 1:
            raise ValueError(
                "noise_probability must be between 0 and 1."
            )