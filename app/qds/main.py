from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.qds.attack_experiment import run_attack_experiment


app = FastAPI(
    title="Q-SENTRY",
    description="Quantum Digital Signature Security Testing Framework",
    version="1.0.0",
)


class ExperimentRequest(BaseModel):
    message_bit: int = Field(default=0, ge=0, le=1)
    basis: str = Field(default="X")
    shots: int = Field(default=1000, gt=0)
    attack: str = Field(default="Z")
    noise: str = Field(default="PHASE_FLIP")
    noise_probability: float = Field(default=0.05, ge=0.0, le=1.0)
    threshold: float = Field(default=0.058, ge=0.0, le=1.0)
    seed: int = Field(default=42)


@app.get("/")
def root():
    return {
        "system": "Q-SENTRY",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/api/experiment")
def run_experiment(request: ExperimentRequest):

    result = run_attack_experiment(
        message_bit=request.message_bit,
        basis=request.basis.upper(),
        shots=request.shots,
        attack=request.attack.upper(),
        threshold=request.threshold,
        seed=request.seed,
        noise=request.noise.upper(),
        noise_probability=request.noise_probability,
    )

    normal = result["normal_with_noise"]
    attack = result["attack_with_noise"]

    normal_detection = normal["detection"]
    attack_detection = attack["detection"]

    return {
        "configuration": {
            "message_bit": request.message_bit,
            "basis": request.basis.upper(),
            "shots": request.shots,
            "attack": request.attack.upper(),
            "noise": request.noise.upper(),
            "noise_probability": request.noise_probability,
            "threshold": request.threshold,
        },
        "normal": {
            "observed_probabilities": normal["observed_probabilities"],
            "tvd": normal_detection["total_variation_distance"],
            "status": normal_detection["status"],
        },
        "attack": {
            "attack_type": request.attack.upper(),
            "observed_probabilities": attack["observed_probabilities"],
            "tvd": attack_detection["total_variation_distance"],
            "status": attack_detection["status"],
        },
        "security_evidence": {
            "normal_status": normal_detection["status"],
            "attack_status": attack_detection["status"],
            "threshold": request.threshold,
            "interpretation": (
                "An anomalous result indicates statistical "
                "deviation from expected behaviour and does "
                "not automatically prove a specific attack."
            ),
        },
    }