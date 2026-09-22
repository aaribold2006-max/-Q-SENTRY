from app.qds.qds_protocol import run_qds_protocol
from app.qds.baseline import generate_baseline
from app.qds.calibration import calibrate_candidate_threshold


print("\n===== Q-SENTRY NOISY BASELINE CALIBRATION =====")


# ---------------------------------------------------------
# Step 1: Generate a legitimate QDS state
# ---------------------------------------------------------

protocol = run_qds_protocol(
    message_bit=0,
    basis="X",
    shots=1000,
    attack=None,
    rng=None,
)


expected = protocol["expected_probabilities"]
state = protocol["receiver_state"]


print("\nExpected distribution:")
print(expected)


# ---------------------------------------------------------
# Step 2: Generate legitimate baseline
#         under 5% phase-flip noise
# ---------------------------------------------------------

baseline = generate_baseline(
    expected=expected,
    shots_per_run=1000,
    runs=100,
    seed=42,
    state=state,
    basis="X",
    noise="PHASE_FLIP",
    noise_probability=0.05,
)


print("\n--- NOISY BASELINE ---")

print(
    "Number of experiments:",
    len(baseline["experiments"]),
)

print(
    "Noise:",
    baseline["noise"],
)

print(
    "Noise probability:",
    baseline["noise_probability"],
)

print(
    "Mean TVD:",
    baseline["mean_tvd"],
)

print(
    "Standard deviation:",
    baseline["std_tvd"],
)

print(
    "Maximum TVD:",
    baseline["max_tvd"],
)


# ---------------------------------------------------------
# Step 3: Calibrate candidate threshold
# ---------------------------------------------------------

calibration = calibrate_candidate_threshold(
    baseline=baseline,
    percentile=95,
)


print("\n--- CALIBRATION ---")

print(
    "Candidate threshold:",
    calibration["candidate_threshold"],
)

print(
    "Percentile:",
    calibration["percentile"],
)