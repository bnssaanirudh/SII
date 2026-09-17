# Experimental Results Audit — Best Available User Runs

## Executive assessment

The uploaded results are useful and several are already strong enough to support the theory qualitatively. They are **not yet uniformly publication-scale**. The strongest current evidence is the 2,500-trial binary benchmark, 5,000-trial false-unlock calibration, the 300-instance LP verification, 2,000-trial robustness runs, and the real UCI HAR binary replay. The multihypothesis and six-class external extensions need additional work before being used as positive headline evidence.

## Provenance used in this consolidated package

- Binary theory / PoC / calibration / finite-confidence: `8153dab2-2b86-4e09-93ba-f104fa2e208d.zip` (standard run: 2,500 trials/config; false-unlock calibration 5,000).
- Multihypothesis: `2d43bbfe-4a38-46af-a3e3-9305e4f8b90d.zip` (standard run: 60 trials/config).
- Record-envelope LP / ladder depth / trap: `033df69a-2838-465b-81dc-4074aec1f931.zip` (300 random LP instances; standard ladder run).
- Robustness and real UCI HAR replay: `4e60dd19-a549-40b1-9f6f-686ee0b0d07c.zip` (2,000 robustness trials/config; 300 binary UCI replay trials/class; 25 six-class trials/class).

All five uploaded ZIP archives passed ZIP integrity checks.

## Key quantitative findings

### 1. Binary lower-bound tightness
Under H0, the proposed running-max procedure approaches the information lower bound as confidence tightens:

|   delta |   mean_tau |    LB_H0 |   LB_ratio |   error_rate |   failed_unlock_rate |
|--------:|-----------:|---------:|-----------:|-------------:|---------------------:|
|   0.1   |    12.2992 |  8.18685 |    1.50231 |       0.0672 |               0.0552 |
|   0.05  |    18.428  | 13.675   |    1.34757 |       0.0356 |               0.0324 |
|   0.01  |    27.6604 | 24.7903  |    1.11578 |       0.014  |               0.0128 |
|   0.001 |    40.0384 | 38.4295  |    1.04187 |       0      |               0      |

The mean/LB ratio decreases from **1.502** at delta=0.1 to **1.042** at delta=0.001. This is good empirical support for first-order tightness.

### 2. Anytime false-unlock calibration

|   alpha_target |   delta |    n |   false_unlock |      fu_lo |     fu_hi |   err_H0 |   err_H1 |
|---------------:|--------:|-----:|---------------:|-----------:|----------:|---------:|---------:|
|           0.1  |   0.001 | 5000 |         0.088  | 0.0804605  | 0.096172  |   0.0002 |   0.0004 |
|           0.05 |   0.001 | 5000 |         0.0424 | 0.0371572  | 0.0483454 |   0      |   0.0006 |
|           0.01 |   0.001 | 5000 |         0.0088 | 0.00656204 | 0.0117922 |   0.0008 |   0.0006 |

Every observed false-unlock rate is below its target alpha, and the 95% confidence intervals are also below the target in these three standard-run configurations.

### 3. One terminal-error point needs rerunning
At delta=0.01 under H0, the observed error was **0.0140** with 95% CI approximately **[0.0101, 0.0194]**, slightly above the nominal target. The simulator uses the exact LLR and the theoretically valid boundary, so this can still be a Monte Carlo fluctuation; however, it should be rerun at FULL_RUN scale before the manuscript states empirical terminal-error calibration at that point.

### 4. Finite-confidence convergence

|   delta |   emp_mean_tau |   L_delta |   emp_over_LB |   boundary_factor |   overshoot_factor |   total_factor |
|--------:|---------------:|----------:|--------------:|------------------:|-------------------:|---------------:|
|   0.1   |        12.1992 |   8.18685 |       1.4901  |           1.57014 |            1.61261 |        2.53202 |
|   0.05  |        18.7388 |  13.675   |       1.3703  |           1.22297 |            1.47087 |        1.79882 |
|   0.01  |        27.2688 |  24.7903  |       1.09998 |           1.03706 |            1.30631 |        1.35472 |
|   0.001 |        40.7232 |  38.4295  |       1.05969 |           1.00349 |            1.2042  |        1.2084  |

The empirical mean/LB ratio falls from **1.490** to **1.060**, matching the paper's finite-confidence-to-asymptotic story.

### 5. Record-envelope theorem verified numerically
Across **300** random LP instances, the largest absolute difference between the numerical LP optimum and the closed-form record-envelope solution was **7.105e-15**. This is effectively numerical equality.

### 6. Price of Certification

| regime    |   theoretical_PoC |   empirical_PoC |   relative_abs_error |
|:----------|------------------:|----------------:|---------------------:|
| easy      |           1.87438 |         1.98152 |           0.0571628  |
| moderate  |           4.6435  |         4.13914 |           0.108616   |
| hard      |           7.33276 |         7.39572 |           0.00858567 |
| very_hard |          15.4321  |        13.9975  |           0.092965   |
| large_gap |          22.4914  |        11.641   |           0.482423   |

Four regimes are reasonably close at delta=.01; the `large_gap` regime is not yet in its asymptotic regime and deviates by roughly **48.2%**. Do not present all five as a uniformly tight finite-delta match without qualification.

### 7. Robustness outside assumptions
Correlation produces the expected degradation: maximum observed error rises from **0.011** at iid correlation 0 to **0.259** at correlation .8. Misspecification likewise raises false-unlock rates and changes stopping times. These are useful *stress tests*, not theorem-validation results.

### 8. External UCI HAR replay
Binary replay is promising:

| policy    |   true_class |   mean_tau |   error_rate |   mean_Nweak |   mean_Nstrong |   unlock_rate |
|:----------|-------------:|-----------:|-------------:|-------------:|---------------:|--------------:|
| gated     |            2 |    3.19667 |         0    |      2.52333 |       0.673333 |     1         |
| gated     |            3 |    4.39333 |         0    |      4.25667 |       0.136667 |     0.0766667 |
| oracle    |            2 |    1.24333 |         0    |      0       |       1.24333  |     1         |
| oracle    |            3 |    1.32333 |         0    |      0       |       1.32333  |     1         |
| weak_only |            2 |    3.31    |         0    |      3.31    |       0        |     0         |
| weak_only |            3 |    4.99667 |         0.04 |      4.99667 |       0        |     0         |

The six-class exploratory extension is currently weak:

|   true_class |   mean_tau |   error_rate |   strong_use |
|-------------:|-----------:|-------------:|-------------:|
|            1 |      77.96 |         0.36 |        57.92 |
|            2 |      94.56 |         0.44 |        71.24 |
|            3 |     122.84 |         0.44 |        81.56 |
|            4 |      29.76 |         0    |         4.36 |
|            5 |     106    |         0.24 |        13.76 |
|            6 |     112.28 |         0.84 |        58.96 |

It should be treated as a limitation / open extension unless redesigned and rerun; class 6 reaches 84% error in the current simple multihypothesis replay.

## What is safe to put in the main paper now

Use the binary lower-bound curve, first-order convergence, false-unlock calibration, finite-confidence decomposition, numerical LP equality, and the binary UCI HAR replay. Use the correlation/misspecification results in a robustness subsection or supplement. Keep multihypothesis switching and six-class UCI in supplementary/limitations until rerun at larger scale and improved.

## Reruns required before final submission

1. `01_binary_theory_benchmarks.ipynb` in `FULL_RUN=1` — especially delta=.01, 1e-4, 1e-5 and large-gap PoC.
2. `02_record_envelope_lp_ladders.ipynb` in `FULL_RUN=1` — 1,000 LP instances and 2,000 trials per ladder depth.
3. `03_multihypothesis_extension.ipynb` in `FULL_RUN=1` — 500 trials/config; consider redesigning N=10 switching to avoid excessively long/censored runs.
4. `05_external_uci_har_replay.ipynb` in `FULL_RUN=1` — 2,000 binary trials/class and 100 six-class trials/class. The six-class method itself likely needs improvement, not merely more trials.

## Bottom line

The results already support the paper's **core binary/statistical theory** well. They do **not** yet justify a broad claim that the framework is solved for general multihypothesis or real-world active sensing. That narrower conclusion is scientifically stronger and is aligned with the paper's stated theorem assumptions.
