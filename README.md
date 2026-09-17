# Evidence-Gated Sequential Learning (SII)

Reproducibility release for the manuscript **“Gated Sequential Learning: Certification Ladders for Binary Identification under Endogenous Experiment Availability.”**

## Scope
The sharp theory is for binary fixed-confidence identification with irreversible nested evidence-gated experiment access. The release validates the record-envelope lower bound, first-order convergence, price of certification, anytime false-unlock control, robustness outside assumptions, and two offline UCI sensing replays.

## Experiment suite
1. `01_binary_theory_benchmarks.ipynb`
2. `02_record_envelope_lp_ladders.ipynb`
3. `03_multihypothesis_extension.ipynb`
4. `04_robustness_stress_tests.ipynb`
5. `05_external_uci_har_replay.ipynb`
6. `06_reviewer_closure_experiments.ipynb`
7. `07_real_external_multisensor_gating_calibrated.ipynb`

The revised Notebook 07 uses subjects 1–6 for fitting, reserves subject 7 for a pre-specified plug-in threshold-calibration follow-up, and keeps subject 8 as untouched test data. The manuscript retains the original uncalibrated subject-8 results for transparency; it does not post-hoc tune on subject 8.

## Headline external result
On UCI Daily and Sports Activities, ascending-vs-descending stairs at nominal `delta=0.05`:
- proposed gated observed error: 0.015
- all-sensor oracle observed error: 0.015
- proposed gated mean cumulative sensor cost: 2.282
- oracle mean cumulative sensor cost: 5.095
- relative cost reduction: 55.2%
- stratified bootstrap 95% interval: 52.8%–57.6%

The stricter `delta=0.01` gated replay has observed error 0.019 (95% Wilson interval 0.0122–0.0295). This calibration miss is retained as a limitation.

## Evidence boundaries
- Smoke/mock outputs are never used as manuscript evidence.
- The two UCI evaluations are offline replays, not prospective physical-safety validation.
- Multihypothesis switching and the six-class external experiment are exploratory stress tests, not theorem extensions.
- The complete submission archive contains fixed configurations, result tables, figures, unit tests, and SHA-256 manifests.

## Data
- UCI Human Activity Recognition Using Smartphones: DOI `10.24432/C54S4K`
- UCI Daily and Sports Activities: DOI `10.24432/C5C59F`

## Reproduction
```bash
pip install -r code/requirements.txt
pytest code/tests/test_core.py
cd code
python run_all.py --mode standard
```

The publication-scale configuration is available through `python run_all.py --mode full`.
