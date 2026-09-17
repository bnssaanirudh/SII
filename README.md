# Evidence-Gated Sequential Learning (SII)
*Robust Action Ladders, Record-Envelope Lower Bounds, and Multi-Sensor Active Sensing Benchmarks*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](code/tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Verification](https://img.shields.io/badge/Reproducibility-Audited%20%26%20Verified-success.svg)](qa_and_audits/)

---

## 📌 Overview

This repository contains the complete theoretical validation suite, simulation engine, audited results, and real-world sensing replays for **Evidence-Gated Sequential Learning**.

In sequential hypothesis testing and active decision-making, an agent dynamically selects from an *action ladder*—a hierarchy of sensing or computation modes ranging from cheap/weak signals to expensive/informative measurements. This codebase rigorously evaluates **irreversible evidence gating**, where the system escalates to higher sensing tiers only upon crossing rigorous confidence thresholds driven by the running maximum of evidence ($M_t = \max_{s \le t} S_s$).

### Core Theoretical Contributions
1. **Record-Envelope Lower Bounds & LP Equivalence**: Closed-form derivation and linear programming formulation for minimum expected sampling cost under nested prefix-constrained information structures.
2. **Price of Certification (PoC)**: Exact characterization of the efficiency ratio between gated sequential testing and the unconstrained oracle as error tolerance $\delta \to 0$.
3. **Escaping the Epistemic Trap**: Demonstrating that reversible policies suffer severe oscillatory overhead and instability under noisy observations, whereas irreversible evidence gating prevents relocking penalties while strictly bounding false-escalation risk ($\le \alpha$).
4. **Real-World Multi-Sensor Replay**: Empirical validation on benchmark multi-sensor activity datasets (UCI HAR and UCI Daily & Sports Activities), achieving a **55.2% reduction in mean sensor cost** while maintaining target statistical fidelity.

---

## 🗂 Repository Structure

```text
.
├── README.md                      # Primary project documentation & reproduction guide
├── RESULTS_SUMMARY.md             # Comprehensive tabulated metrics across all regimes
├── HEADLINE_RESULTS.csv           # Key quantitative summary metrics
├── NOTEBOOK_TO_RESULTS_MAP.csv    # Mapping between Jupyter notebooks and result artifacts
├── CHAT_STAGE_MAP.md              # Research evolution & chat-stage provenance record
├── FILE_MANIFEST_SHA256.csv       # Cryptographic SHA-256 integrity hashes for all files
│
├── code/                          # Executable source code, notebooks, and tests
│   ├── notebooks/                 # 7 Chronological experimental notebooks
│   │   ├── 01_binary_theory_benchmarks.ipynb
│   │   ├── 02_record_envelope_lp_ladders.ipynb
│   │   ├── 03_multihypothesis_extension.ipynb
│   │   ├── 04_robustness_stress_tests.ipynb
│   │   ├── 05_external_uci_har_replay.ipynb
│   │   ├── 06_reviewer_closure_experiments.ipynb
│   │   └── 07_real_external_multisensor_gating.ipynb
│   ├── src/                       # Core library
│   │   └── gated_benchmarks.py    # Sequential tests, KL divergence, LP solvers, simulation engine
│   ├── tests/                     # Unit test suite
│   │   └── test_core.py           # Invariant, LP, and statistical verification tests
│   ├── EXPERIMENTAL_PROTOCOL.md   # Step-by-step experimental design specifications
│   ├── EXPERIMENT_MATRIX.csv      # Parameter configurations across all test suites
│   ├── requirements.txt           # Python dependencies
│   ├── run_all.py                 # CLI multi-mode experiment runner
│   ├── make_notebooks.py          # Notebook generator and parameterizer
│   └── verify_package.py          # Package integrity verifier
│
├── results/                       # Audited and categorized experiment outputs
│   ├── audited_best/              # Curated primary publication-grade results and figures
│   ├── core_suite/                # Base theoretical and simulation benchmarks
│   ├── reviewer_closure/          # High-sample rare-event follow-up & sensitivity sweeps
│   └── external_multisensor/      # Real-data DSADS multi-sensor benchmark outputs
│
├── qa_and_audits/                 # Quality assurance, test logs, and audit reports
│   ├── RESULTS_AUDIT.md           # Comprehensive data audit & anomaly investigation
│   ├── NOTEBOOK07_REAL_DATA_AUDIT.md # Verification of genuine multi-sensor dataset runs
│   ├── unit_test_output.txt       # Pytest execution verification logs
│   └── zip_integrity.txt          # Archive checksum verification logs
│
├── historical_raw_results/        # Untouched raw result ZIP archives for full provenance
└── original_packages/             # Verified standalone benchmark distributions
```

---

## 🔬 Experiment Notebooks Chronology

| Notebook | Title | Core Objective | Key Findings |
|---|---|---|---|
| **01** | `01_binary_theory_benchmarks.ipynb` | First-order lower-bound convergence | Mean/LB ratio falls from $1.50$ ($\delta=0.1$) to $1.04$ ($\delta=0.001$), confirming first-order asymptotic optimality. |
| **02** | `02_record_envelope_lp_ladders.ipynb` | Record-envelope LP & Epistemic Trap | 300 random prefix LPs match theoretical closed-form solution to $\approx 7.1 \times 10^{-15}$ precision. Demonstrates trap avoidance. |
| **03** | `03_multihypothesis_extension.ipynb` | Multi-hypothesis active testing | Evaluates matrix games, GLR, and hardest-alternative switching across multi-class action ladders. |
| **04** | `04_robustness_stress_tests.ipynb` | Out-of-model stress testing | Stress tests performance under autoregressive correlation ($\text{AR}(1)$), model misspecification, and discrete overshoot. |
| **05** | `05_external_uci_har_replay.ipynb` | First external dataset replay | Offline sensing replay on UCI HAR smartphone accelerometer/gyroscope signals (Walking Upstairs vs. Downstairs). |
| **06** | `06_reviewer_closure_experiments.ipynb` | Reviewer closure & rare events | 10,000-trial rare false-unlock calibration ($\alpha \le 0.01$), terminal error validation, and cap sensitivity sweeps. |
| **07** | `07_real_external_multisensor_gating.ipynb` | 5-Level sensor ladder on DSADS | Real-data multi-sensor replay on UCI Daily and Sports Activities (torso $\to$ arms $\to$ legs); **55.2% sensor cost reduction**. |

---

## 📊 Key Quantitative Results

### 1. Binary Asymptotic Efficiency ($\delta \to 0$)
As error tolerance $\delta$ decreases, the ratio of empirical stopping time to the theoretical record-envelope lower bound converges toward unity ($1.00$):

| Target $\delta$ | Empirical Mean Stopping Time | Theoretical Lower Bound | Ratio ($\text{Mean} / \text{LB}$) | $H_0$ Error |
|:---:|:---:|:---:|:---:|:---:|
| `0.100` | 12.299 | 8.187 | **1.502** | 0.0672 |
| `0.050` | 18.428 | 13.675 | **1.348** | 0.0356 |
| `0.010` | 27.660 | 24.790 | **1.116** | 0.0140 |
| `0.001` | 40.038 | 38.430 | **1.042** | 0.0000 |

### 2. Rare-Event False Unlock Calibration
Empirical evaluation with $N = 10,000$ independent trials verifying strict false-unlock control beneath specified bounds:

| Target $\alpha$ | Trials ($N$) | Observed False Unlock Rate | 95% Wilson Confidence Interval | Status |
|:---:|:---:|:---:|:---:|:---:|
| `0.0100` | 10,000 | **0.0073** | $[0.00581, 0.00917]$ | Strict bound satisfied ($\le 0.01$) |
| `0.0010` | 10,000 | **0.0009** | $[0.00047, 0.00171]$ | Resolution-limited |
| `0.0001` | 10,000 | **0.0000** | $[0.00000, 0.00038]$ | Resolution-limited |

### 3. Record-Envelope LP Equivalence
- **Evaluated**: 300 random prefix-constrained LP ladder instances.
- **Result**: Maximum absolute discrepancy between numerical HiGHS LP solver and closed-form record-envelope solution was **$7.105 \times 10^{-15}$** (machine precision).

### 4. Real-World Multi-Sensor Benchmark (UCI DSADS)
Hierarchical ladder across 5 sensor placements (Torso $\to$ Right Arm $\to$ Left Arm $\to$ Right Leg $\to$ Left Leg):
- **Target $\delta = 0.05$**: Gated error = **$0.015$** (matching All-Sensor Oracle error of $0.015$).
- **Resource Efficiency**: Proposed gated policy achieved mean sensor cost of **$2.282$** vs. Oracle cost of **$5.095$** (**$55.2\%$ cost reduction**).

---

## ⚠️ Evidence Boundaries & Scientific Caveats

To ensure scientific integrity, findings are categorized into strict evidence tiers:
* **Theorem-Validated Evidence**: Binary first-order convergence, record-envelope LP equivalence, false-unlock calibration, and price-of-certification asymptotic scaling.
* **External Empirical Replays**: Notebook 05 and Notebook 07 are offline sensor replay evaluations using plug-in likelihood models, representing empirical validation rather than prospective physical trials.
* **Stress Tests**: Notebook 04 and multi-class scaling analyze performance outside theoretical assumptions (e.g. cross-subject sensor misspecification, correlated noise).
* **Provenance Note**: Early historical development traces contain a mock 6-class HAR fallback, which is explicitly tagged as `mock fallback — NOT REPORTABLE` in historical logs and excluded from all reported empirical claims (see [RESULTS_SUMMARY.md](RESULTS_SUMMARY.md) & [qa_and_audits/RESULTS_AUDIT.md](qa_and_audits/RESULTS_AUDIT.md)).

---

## 🚀 Quickstart & Reproduction

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/bnssaanirudh/SII.git
cd SII
pip install -r code/requirements.txt
```

### 2. Run Test Suite
Verify that all unit tests and mathematical invariants pass:
```bash
pytest code/tests/test_core.py
```

### 3. Run Benchmark Suite
Run experiments across desired execution tiers:
```bash
cd code

# Fast sanity check (~30 seconds)
python run_all.py --mode smoke

# Standard publication reproduction
python run_all.py --mode standard

# High-statistic publication-scale run
python run_all.py --mode full
```

### 4. Package Verification
Verify archive consistency and notebook JSON formats:
```bash
python code/verify_package.py
```

---

## 📚 Datasets & Citations

The real-world sensor replays in this benchmark utilize:
1. **UCI Human Activity Recognition Using Smartphones Dataset**  
   *DOI*: [`10.24432/C54S4K`](https://doi.org/10.24432/C54S4K)
2. **UCI Daily and Sports Activities Dataset (DSADS)**  
   *DOI*: [`10.24432/C5C59F`](https://doi.org/10.24432/C5C59F)

---

## 📄 License

This codebase is licensed under the [MIT License](LICENSE).
