# Notebook 07 real-data audit and manuscript update

## Result provenance
- Dataset: UCI Daily and Sports Activities
- DOI: 10.24432/C5C59F
- Metadata in the uploaded result bundle: `real_data=true`, `smoke_test=false`, `full_run=false`
- Training subjects: 1-6
- Held-out test subject: 8
- Binary task: ascending stairs vs descending stairs
- Six-class task: sitting, standing, ascending stairs, descending stairs, walking in parking lot, treadmill running
- Stopping cap: 100
- No cap hits in the reported external runs

## Main reportable binary result
At delta=0.05:
- Proposed gated: error 0.015, mean stopping time 1.404, mean cumulative sensor cost 2.282
- All-sensor oracle: error 0.015, mean stopping time 1.019, mean cost 5.095
- Weak-only: error 0.039, mean stopping time 1.426, mean cost 1.426

Thus the gated procedure matches the oracle's observed binary error while using about 55.2% less cumulative sensor cost.

At delta=0.01:
- Proposed gated error: 0.019, 95% Wilson CI [0.0122, 0.0295]
- Oracle error: 0.000 in 1,000 trials
- Weak-only error: 0.029

The gated result does not meet the nominal 1% target. This is reported as evidence that estimated cross-subject observation models do not inherit the exact likelihood-ratio calibration assumed by the theory.

## Six-class exploratory result
At delta=0.01:
- Proposed gated error: 0.1389
- Weak-only error: 0.1667
- Fixed schedule error: 0.1667
- Reversible-posterior error: 0.1422
- All-sensor oracle error: 0.1822

The aggregate gated result improves over weak-only and full-sensor baselines, but performance is highly class-dependent. The walking-parking class has error 0.8267 and accounts for most mistakes. This is therefore used as a multihypothesis/representation-shift stress test, not theorem validation.

## Stage occupancy
For the proposed six-class gated policy:
- L1: 51.8%
- L2: 15.5%
- L3: 20.7%
- L4: 5.5%
- L5: 6.5%

This supports the staged resource-allocation interpretation: most sequential observations remain at the lower-cost sensing levels.

## Manuscript changes
Both STRF and Machine Learning drafts now:
- add the five-level body-sensor benchmark;
- cite the UCI dataset and its original Pattern Recognition paper;
- distinguish positive binary external evidence from mixed six-class evidence;
- explicitly state the failure to meet nominal delta=0.01 under cross-subject model shift;
- update data availability from one to two UCI datasets;
- update reproducibility package from six to seven notebooks;
- update cover letters and the MLJ contribution sheet.

## Verification
- Main manuscripts compile successfully.
- 27 cited keys = 27 bibliography entries in each manuscript.
- No missing or orphan citations.
- No unresolved references.
- No overfull boxes in the final compile.
- Main PDFs: 27 pages each.
- MLJ contribution sheet: 2 pages.
- MLJ cover letter: 1 page.
- STRF cover letter: 1 page.
- PDF preflight: openable, searchable, unencrypted, no XFA.
