# Final reviewer-closure update audit

## Incorporated into both manuscripts

- 10,000-run rare false-unlock calibration: target alpha=0.01 -> observed 0.0073, 95% CI [0.0058, 0.0092].
- Lower-probability false-unlock checks at alpha=0.001 and 0.0001, explicitly described as resolution-limited where the interval does not certify the nominal target.
- Terminal-error follow-up at delta=0.01, 0.001, 0.0001 with 2,500 trials per hypothesis; the 1e-4 case is explicitly not claimed as resolved by Monte Carlo.
- Stopping-cap sensitivity: caps 50/100 distort results; cap-hit rates are negligible from about 250 onward in the binary benchmark.
- Certification-threshold sensitivity at delta=1e-3 over rho={0.1,0.3,0.5,0.7,0.9}; empirical PoC tracks the first-order trend.
- Extreme information-gap PoC follow-up, reported as slow/non-uniform finite-confidence convergence rather than a positive match.
- Higher-budget synthetic multihypothesis diagnostics (120 trials/configuration): uniformly-hardest cases remain stable, while N=10 hardest-alternative switching can saturate the 3,000-step cap.

## Deliberately excluded from manuscript evidence

- The Notebook 06 six-class HAR output, because the result files state `mock fallback — NOT REPORTABLE`. The previously completed genuine UCI HAR binary replay remains in both manuscripts.

## Verification

- STRF manuscript: 26 pages, searchable, PDF preflight clean, no undefined references or overfull-box errors.
- Machine Learning manuscript: 26 pages, searchable, PDF preflight clean, no undefined references or overfull-box errors.
- MLJ Contribution Information Sheet: 2 pages.
- MLJ cover letter: 1 page.
- STRF cover letter: 1 page.
- Existing bibliography count remains unchanged because no new literature claim was introduced by the closure experiments.

## Readiness assessment

### Statistical Theory and Related Fields
Submission-ready after author-specific fields (email, funding, competing interests) are confirmed. The main residual empirical limitations are finite Monte Carlo resolution at delta=1e-4 and non-uniform PoC convergence in the deliberately extreme information-gap regime; both are now disclosed rather than hidden.

### Machine Learning
Technically coherent and materially stronger than the previous version. It is reasonable to submit, but journal-fit risk is still higher than for STRF because the sharp theory is binary and the positive external evaluation is an offline two-class sensing replay rather than a broad active-learning benchmark. The multihypothesis failure modes are honestly characterized as open problems.
