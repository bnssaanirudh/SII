"""Subject-7 calibration follow-up for Notebook 07.

Usage
-----
Execute `07_real_external_multisensor_gating.ipynb` through the model/engine
cells first, then run this file in the same namespace (for example with
`%run -i code/notebooks/07_subject7_calibration_followup.py`).

Design
------
- subjects 1--6: model fitting (unchanged from Notebook 07)
- subject 7: threshold-scale selection only
- subject 8: untouched evaluation after the scale is frozen

The routine never chooses a scale from subject-8 performance. It exports the
calibration path and the final subject-8 summary as separate files so that the
original uncalibrated manuscript result remains auditable.
"""

required = [
    "BINARY_MODELS", "BINARY_ACTIVITIES", "META", "XLEVEL", "LEVEL_COST",
    "RHO", "SEED", "RESULTS", "wilson_interval", "mean_ci",
    "softmax_from_log", "np", "pd", "math"
]
missing = [name for name in required if name not in globals()]
if missing:
    raise RuntimeError(
        "Run Notebook 07 first in the same kernel. Missing globals: " + ", ".join(missing)
    )

CAL_SUBJECTS = [7]
TEST_SUBJECTS = [8]


def sequential_trial_for_subjects(true_class, models, delta, method, rng,
                                  subject_ids, threshold_scale=1.0,
                                  fixed_upgrade_every=6, max_steps=None):
    if max_steps is None:
        max_steps = globals().get("MAX_STEPS", 100)

    classes = models[1].classes_
    K = len(classes)
    A = threshold_scale * (math.log((K - 1) / delta) if K > 2 else math.log(1 / delta))
    gate_thresholds = [rho * A for rho in RHO]

    mask = META.subject.isin(subject_ids) & (META.activity == true_class)
    candidates = np.flatnonzero(mask)
    if len(candidates) == 0:
        raise RuntimeError(f"No segments for class {true_class}, subjects={subject_ids}")

    cum = np.zeros(K)
    level = 1
    max_level = 1
    stage_counts = np.zeros(5, dtype=int)
    total_sensor_cost = 0.0
    unlock_times = [np.nan] * 4
    perm = rng.permutation(candidates)
    ptr = 0

    for t in range(1, max_steps + 1):
        if ptr >= len(perm):
            perm = rng.permutation(candidates)
            ptr = 0
        idx = perm[ptr]
        ptr += 1

        if method == "oracle_all":
            level = 5
        elif method == "weak_only":
            level = 1
        elif method == "fixed_schedule":
            level = min(5, 1 + (t - 1) // fixed_upgrade_every)
        elif method == "reversible_posterior":
            if t > 1:
                conf = np.max(softmax_from_log(cum))
                cuts = [0.65, 0.75, 0.85, 0.93]
                level = min(5, 1 + sum(conf >= c for c in cuts))
        elif method == "proposed_gated":
            level = max_level
        else:
            raise ValueError(method)

        ll = models[level].loglik(XLEVEL[level][idx:idx + 1])[0]
        cum += ll
        stage_counts[level - 1] += 1
        total_sensor_cost += LEVEL_COST[level]

        order = np.argsort(cum)
        best, second = order[-1], order[-2]
        margin = cum[best] - cum[second]

        if method == "proposed_gated":
            while max_level < 5 and margin >= gate_thresholds[max_level - 1]:
                unlock_times[max_level - 1] = t
                max_level += 1
            level = max_level

        if margin >= A:
            pred = int(classes[best])
            return {
                "true": int(true_class), "pred": pred,
                "error": int(pred != true_class), "tau": t,
                "sensor_cost": total_sensor_cost, "final_level": int(level),
                "stage_counts": stage_counts.tolist(),
                "unlock_times": unlock_times, "capped": 0,
            }

    pred = int(classes[int(np.argmax(cum))])
    return {
        "true": int(true_class), "pred": pred,
        "error": int(pred != true_class), "tau": max_steps,
        "sensor_cost": total_sensor_cost, "final_level": int(level),
        "stage_counts": stage_counts.tolist(),
        "unlock_times": unlock_times, "capped": 1,
    }


def evaluate(subject_ids, delta, threshold_scale, n_trials_per_class, seed_offset):
    rows = []
    for c in BINARY_ACTIVITIES:
        for r in range(n_trials_per_class):
            rrng = np.random.default_rng(
                SEED + seed_offset + int(delta * 1e6) + 1000 * c + 17 * r
            )
            out = sequential_trial_for_subjects(
                c, BINARY_MODELS, delta, "proposed_gated", rrng,
                subject_ids=subject_ids, threshold_scale=threshold_scale,
            )
            out.update({
                "delta": delta, "method": "proposed_gated",
                "threshold_scale": threshold_scale, "rep": r,
                "subjects": "-".join(map(str, subject_ids)),
            })
            rows.append(out)
    return pd.DataFrame(rows)


def choose_scale(delta, grid=None, n_trials_per_class=400):
    if grid is None:
        grid = np.round(np.arange(1.0, 2.51, 0.10), 2)
    records = []
    chosen = None
    for j, scale in enumerate(grid):
        df = evaluate(
            CAL_SUBJECTS, delta, float(scale), n_trials_per_class,
            seed_offset=700000 + 10000 * j,
        )
        k = int(df.error.sum())
        n = len(df)
        lo, hi = wilson_interval(k, n)
        records.append({
            "delta": delta, "threshold_scale": float(scale), "n": n,
            "error_rate": k / n, "error_ci_lo": lo, "error_ci_hi": hi,
            "mean_tau": float(df.tau.mean()),
            "mean_sensor_cost": float(df.sensor_cost.mean()),
            "cap_rate": float(df.capped.mean()),
            "meets_nominal_by_upper_ci": bool(hi <= delta),
        })
        if hi <= delta:
            chosen = float(scale)
            break
    if chosen is None:
        chosen = float(grid[-1])
    return chosen, pd.DataFrame(records)


def summarize_test(df):
    rows = []
    for (delta, scale), g in df.groupby(["delta", "threshold_scale"]):
        k = int(g.error.sum())
        n = len(g)
        elo, ehi = wilson_interval(k, n)
        mt, tlo, thi = mean_ci(g.tau)
        mc, clo, chi = mean_ci(g.sensor_cost)
        rows.append({
            "delta": delta, "threshold_scale": scale, "n_trials": n,
            "error_rate": k / n, "error_ci_lo": elo, "error_ci_hi": ehi,
            "mean_tau": mt, "tau_ci_lo": tlo, "tau_ci_hi": thi,
            "mean_sensor_cost": mc, "sensor_cost_ci_lo": clo,
            "sensor_cost_ci_hi": chi, "cap_rate": float(g.capped.mean()),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    deltas = globals().get("DELTAS", [0.05, 0.01])
    n_test = globals().get("N_BINARY_TRIALS", 500)

    calibration_tables = []
    test_tables = []
    for delta in deltas:
        scale, table = choose_scale(delta)
        table["chosen_scale"] = scale
        calibration_tables.append(table)
        test_tables.append(
            evaluate(TEST_SUBJECTS, delta, scale, n_test, seed_offset=900000)
        )

    cal = pd.concat(calibration_tables, ignore_index=True)
    test_trials = pd.concat(test_tables, ignore_index=True)
    test_summary = summarize_test(test_trials)

    cal.to_csv(RESULTS / "external_subject7_calibration.csv", index=False)
    test_trials.to_json(
        RESULTS / "external_binary_subject7_calibrated_trials.json",
        orient="records", indent=2,
    )
    test_summary.to_csv(
        RESULTS / "external_binary_subject7_calibrated_summary.csv", index=False
    )

    print("Subject-7 calibration path")
    print(cal.to_string(index=False))
    print("\nFrozen-scale subject-8 evaluation")
    print(test_summary.to_string(index=False))
