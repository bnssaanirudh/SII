# Chat-stage provenance map

This file explains how the recovered testing artifacts correspond to the evolution of the paper work.

## 1. Start / original experiment-building work

Recovered artifacts:
- `code/notebooks/01_binary_theory_benchmarks.ipynb`
- `code/notebooks/02_record_envelope_lp_ladders.ipynb`
- `code/notebooks/03_multihypothesis_extension.ipynb`
- `code/notebooks/04_robustness_stress_tests.ipynb`
- `code/notebooks/05_external_uci_har_replay.ipynb`
- shared library `code/src/gated_benchmarks.py`
- test suite, runners, protocols, and original benchmark package
- original/core result tables and figures

These implement the lower-bound, first-order, PoC, record-envelope, false-unlock, ladder-depth, trap, robustness, multihypothesis, and first UCI HAR replay experiments.

## 2. Main-chat result consolidation and reviewer closure

Recovered artifacts:
- all five historical user result ZIPs used in the consolidated audit
- `results/audited_best/` selecting the strongest trustworthy result versions
- `code/notebooks/06_reviewer_closure_experiments.ipynb`
- actual standard Notebook-06 results under `results/reviewer_closure/`
- smoke-only Notebook-06 verification under `smoke_only/`

Notebook 06 adds rare-event false-unlock calibration, terminal-error follow-up, cap sensitivity, threshold/rho sensitivity, extreme-PoC diagnostics, and higher-stat multihypothesis diagnostics.

## 3. Later branch / real-data strengthening

Recovered artifacts:
- `code/notebooks/07_real_external_multisensor_gating.ipynb`
- genuine real-data Notebook-07 results under `results/external_multisensor/`
- Notebook-07 verification and real-data audit files

Notebook 07 uses UCI Daily and Sports Activities and constructs a five-level torso-to-full-body sensor ladder. The uploaded result metadata records `real_data=true` and `smoke_test=false`.

## 4. Current reviewer/humanization branch

No new numerical experiment notebook was introduced after Notebook 07. The work in this branch focused on integrating the existing evidence into the manuscript, answering reviewer comments, auditing references, and clearly separating reportable results from exploratory/negative/smoke-only evidence. Those evidence-boundary audits are retained under `qa_and_audits/`.
