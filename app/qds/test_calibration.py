from app.qds.baseline import generate_baseline
from app.qds.calibration import calibrate_candidate_threshold


print("\n===== Q-SENTRY BASELINE CALIBRATION =====")


expected = {
    "+": 1.0,
    "-": 0.0,
}


baseline = generate_baseline(
    expected=expected,
    shots_per_run=1000,
    runs=100,
    seed=42,
)


print("\n--- BASELINE ---")

print(
    "Number of experiments:",
    len(baseline["experiments"]),
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