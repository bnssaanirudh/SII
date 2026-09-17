Notebook 06 — Reviewer-Closure Experiments

Run modes:
  Smoke verification: set environment variable SMOKE_TEST=1
  Standard: run normally
  Publication scale: set environment variable FULL_RUN=1

The notebook is standalone: if src/gated_benchmarks.py is absent it creates the verified embedded fallback automatically.
The last cell creates reviewer_closure_results.zip and automatically downloads it in Google Colab.

Main experiments:
- Rare-event terminal-error calibration
- Anytime false-unlock rare-event calibration
- Extreme information-gap PoC convergence
- High-statistics N=3/5/10 multihypothesis tests
- Stopping-cap sensitivity
- Joint rho/delta threshold sensitivity
- Bootstrap uncertainty
- Higher-statistics six-class UCI HAR replay
- Reviewer-facing claim-status table
