# Smoke-only outputs — DO NOT REPORT AS PAPER RESULTS

This directory preserves code-path verification artifacts.

- `reviewer_closure_results_smoke_verified.zip` comes from Notebook 06 smoke verification.
- Notebook 06's six-class HAR fallback is explicitly marked `mock fallback — NOT REPORTABLE`.
- Notebook 07 smoke verification used a deterministic schema-matched surrogate because the verification environment could not download the 162.9 MB UCI Daily and Sports Activities archive. The genuine Notebook 07 real-data results are stored under `../results/external_multisensor/`.

Use smoke outputs only to verify that code executes and output schemas are produced.
