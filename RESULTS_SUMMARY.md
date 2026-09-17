# Results Summary

This summary points to the strongest final evidence while preserving negative and unresolved results. The raw CSV/JSON files remain the source of truth.

## 1. Binary lower-bound / first-order benchmark

| delta | mean stopping time | lower bound | mean/LB | H0 error | failed unlock |
|---:|---:|---:|---:|---:|---:|
| 0.1 | 12.2992 | 8.1868 | 1.5023 | 0.0672 | 0.0552 |
| 0.05 | 18.4280 | 13.6750 | 1.3476 | 0.0356 | 0.0324 |
| 0.01 | 27.6604 | 24.7903 | 1.1158 | 0.0140 | 0.0128 |
| 0.001 | 40.0384 | 38.4295 | 1.0419 | 0.0000 | 0.0000 |

The mean/lower-bound ratio falls from about 1.50 at delta=0.1 to about 1.04 at delta=0.001, supporting the first-order convergence claim. The delta=0.01 H0 point in the 2,500-trial run had error 0.0140 with a 95% interval approximately [0.0101, 0.0194], so it was treated conservatively and followed up rather than hidden.

## 2. False-unlock calibration

| target alpha | n | observed | 95% CI |
|---:|---:|---:|---:|
| 0.1 | 5000 | 0.0880 | [0.0805, 0.0962] |
| 0.05 | 5000 | 0.0424 | [0.0372, 0.0483] |
| 0.01 | 5000 | 0.0088 | [0.0066, 0.0118] |

Reviewer-closure rare-event follow-up:

| target alpha | n | observed | 95% CI |
|---:|---:|---:|---:|
| 0.01 | 10000 | 0.0073 | [0.00581, 0.00917] |
| 0.001 | 10000 | 0.0009 | [0.00047, 0.00171] |
| 0.0001 | 10000 | 0.0000 | [0.00000, 0.00038] |

The alpha=0.01 follow-up is the strongest rare-event calibration result: 0.0073 in 10,000 runs with the full 95% interval below 0.01. The 0.001 and 0.0001 settings are explicitly resolution-limited.

## 3. Record-envelope LP verification

- 300 random prefix-constrained LP instances were checked.
- Maximum absolute discrepancy between the numerical LP and the closed-form record-envelope solution: approximately `7.105e-15`.

## 4. Price of Certification

| regime | theory PoC | empirical PoC |
|---|---:|---:|
| easy | 1.874 | 1.982 |
| moderate | 4.643 | 4.139 |
| hard | 7.333 | 7.396 |
| very_hard | 15.432 | 13.997 |
| large_gap | 22.491 | 11.641 |

Four moderate regimes track the first-order prediction reasonably well at finite confidence. The deliberately extreme `large_gap` regime remains far from its asymptotic limit and is reported as a negative/non-uniform finite-sample result.

## 5. First external replay: UCI HAR

The genuine UCI HAR binary replay uses WALKING_UPSTAIRS vs WALKING_DOWNSTAIRS. It is an offline replay, not physical safety validation.

Key audited rows are in `results/audited_best/results/uci_har_binary_replay.csv`.

## 6. Reviewer-closure follow-up

- Terminal-error follow-up: 2,500 trials per hypothesis at delta 0.01, 0.001, and 0.0001.
- Short stopping caps 50/100 visibly distort results; binary behavior stabilizes once the cap is around 250 or larger.
- Threshold/rho sweeps at delta=0.001 follow the predicted Price-of-Certification trend.
- Higher-stat multihypothesis runs support the uniformly-hardest special case but show severe cap saturation in difficult switching cases.
- Notebook 06 six-class HAR output came from `mock fallback — NOT REPORTABLE` and is retained only for code-path/history verification.

## 7. Second genuine external benchmark: UCI Daily and Sports Activities

- At delta=0.05, proposed gated error = **0.015**; all-sensor oracle error = **0.015**.
- Proposed mean sensor cost = **2.282** vs oracle **5.095**, a **55.2% reduction**.
- Weak-only error at the same target = **0.039**.
- At delta=0.01, proposed gated error is 0.019 with 95% CI [0.0122, 0.0295], so the plug-in cross-subject replay misses the nominal 1% target.

Six-class stress test at delta=0.01:

| method | error | mean tau | mean sensor cost |
|---|---:|---:|---:|
| fixed_schedule | 0.1667 | 3.0944 | 3.3344 |
| oracle_all | 0.1822 | 1.0867 | 5.4333 |
| proposed_gated | 0.1389 | 2.4389 | 4.8589 |
| reversible_posterior | 0.1422 | 2.0456 | 4.7233 |
| weak_only | 0.1667 | 3.1067 | 3.1067 |

The aggregate six-class result is not a theorem validation: the `walking_parking` class has error **0.8267**, dominating the failures.

Stage occupancy for the proposed six-class gated policy:

- Level 1: 51.8%
- Level 2: 15.5%
- Level 3: 20.7%
- Level 4: 5.5%
- Level 5: 6.5%

## 8. Result-status rules

- **Reportable theorem-matched evidence:** binary lower-bound/first-order results, LP equality, false-unlock calibration, finite-confidence decomposition.
- **Reportable external evidence with caveats:** genuine UCI HAR binary replay and Notebook 07 binary five-level replay.
- **Stress tests:** correlation, misspecification, overshoot, six-class replay.
- **Exploratory/open:** general multihypothesis switching.
- **Never report as empirical evidence:** Notebook 06 mock-fallback six-class HAR numbers.

For detailed provenance and caveats, also read `qa_and_audits/RESULTS_AUDIT.md`, `qa_and_audits/FINAL_UPDATE_AUDIT.md`, and `qa_and_audits/NOTEBOOK07_REAL_DATA_AUDIT.md`.