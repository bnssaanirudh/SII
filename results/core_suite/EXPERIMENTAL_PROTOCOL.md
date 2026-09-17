# Submission-Ready Experimental Protocol

## 1. Questions the evaluation must answer

**Q1 — Is the information lower bound predictive?**  Compare the record-envelope lower bound to the proposed running-max LR procedure as confidence increases.

**Q2 — Is the policy first-order optimal numerically?**  Plot `E[tau]/log(1/delta)` and verify convergence toward `C_gate`.

**Q3 — What does certification cost?**  Compare gated vs immediate-access oracle and map theoretical/empirical Price of Certification over information gap and certification fraction.

**Q4 — Is the record envelope structurally necessary?**  Use non-monotone `K_l`, compare the closed form to direct LP solutions, and verify on random instances.

**Q5 — Are the anytime guarantees visible empirically?**  Test false-unlock control under H1 and terminal error under both hypotheses with confidence intervals.

**Q6 — Where does finite-confidence slack come from?**  Separate boundary-design slack, overshoot-bound slack and observed stopping time.

**Q7 — Does the ladder extend beyond two levels?**  Simulate L=2,3,5,10 with nested Bernoulli experiments.

**Q8 — What happens beyond binary hypotheses?**  Test N=3,5,10 in both a uniformly-hardest regime and a hardest-alternative-switching regime.

**Q9 — How fragile are the guarantees to assumption violations?**  Stress test Gaussian increments, dependence and model misspecification.

**Q10 — Can the machinery be instantiated on external data?**  Run UCI HAR weak-vs-strong sensing replay, then optionally PRISM robotics replay.

## 2. Main synthetic benchmark family

### Paper anchor instance

- Weak: H0 ~ Bernoulli(0.7), H1 ~ Bernoulli(0.5)
- Strong: H0 ~ Bernoulli(0.8), H1 ~ Bernoulli(0.2)
- certification exponent: rho=0.4
- delta grid: 1e-1, 5e-2, 1e-2, 1e-3, 1e-4, 1e-5 in full mode

### Difficulty regimes

| Regime | weak `(p0,p1)` | strong `(p0,p1)` | Purpose |
|---|---|---|---|
| Easy | (.80,.20) | (.95,.05) | low absolute complexity |
| Moderate | (.70,.50) | (.80,.20) | manuscript anchor |
| Hard | (.60,.50) | (.70,.30) | weak early evidence |
| Very hard | (.55,.50) | (.65,.35) | near-trap early stage |
| Large gap | (.70,.50) | (.99,.01) | large certification price |

For every regime calculate KL rates analytically from the generating laws; do not estimate them from Monte Carlo.

## 3. Baselines

Use only interpretable baselines:

1. **Oracle** — strongest action from sample 1; infeasible reference.
2. **Weak-only** — never unlock.
3. **Fixed-sample gate** — deterministic weak-sample milestone.
4. **Current-evidence gate** — reversible/non-running-max ablation.
5. **Proposed running-max LR gate** — irreversible certificate.

For multihypothesis experiments also report oracle and weak-only. Do not describe the oracle as a feasible competitor.

## 4. Metrics

Every core configuration should include:

- `E[tau]` and 95% CI;
- median `tau`;
- 95th percentile `tau`;
- `P0(hat H=1)` and `P1(hat H=0)`;
- false-unlock probability and Wilson CI;
- failed-unlock probability under H0;
- `E[N_l]` for each ladder level;
- empirical `E[tau]_gated/E[tau]_oracle`;
- first-order theoretical PoC;
- lower-bound ratio `E[tau]/LB`;
- mean and 95th-percentile overshoot.

## 5. LP / record-envelope benchmark

Use the manuscript counterexample plus alternating and deep non-monotone patterns. Then generate 1,000 random instances in full mode:

- L sampled from 2..10;
- nondecreasing `d_l`;
- arbitrary positive `K_l` (not forced monotone);
- solve original LP numerically;
- compare to `sum_l (Kbar_l-Kbar_{l-1})/d_l`.

Report maximum and median absolute error. The full-mode target is numerical equality up to solver tolerance.

## 6. Multi-level sequential benchmark

For L in {2,3,5,10}:

- H1 action law fixed at Bernoulli(0.5);
- H0 action parameters rise from 0.58 to 0.90;
- certification exponents evenly partition [0,1];
- compare empirical `E[tau]/log(1/delta)` with `C_gate`;
- report stage occupancy and unlock failures.

This validates multi-level behavior without altering the theorem.

## 7. Multihypothesis benchmark

Run N in {3,5,10} under two constructions:

**Uniformly hardest:** one alternative is pointwise closest to H0 for weak and strong actions. This corresponds to the tractable appendix case.

**Switching hardest alternative:** the weak action's closest alternative differs from the strong action's closest alternative. This deliberately leaves the scalar special case.

Use a pairwise-log-likelihood stopping rule and report mean/median/q95 stopping time, error, weak/strong counts and false unlocking.

**Paper language:** call this an exploratory extension. Do not claim the binary matched lower/upper theorem extends to the switching case.

## 8. Robustness outside formal assumptions

### Gaussian
Equal-variance Gaussian channels. Use the asymptotic prediction as a reference, but do not invoke the bounded-increment finite-confidence theorem.

### Correlation
AR(1) latent noise with correlation 0, .1, .3, .5, .8 while the procedure still uses iid likelihoods. Plot error/false unlock vs correlation.

### Misspecification
Shift the model's H1 mean by epsilon in {0,.01,.05,.10}; data remain generated by the nominal model.

### Overshoot
Report the empirical overshoot distribution and compare with the qualitative finite-confidence discussion.

## 9. External benchmark — UCI HAR

Use the official UCI Human Activity Recognition Using Smartphones train/test split.

- six activities;
- weak channel: accelerometer-derived engineered features;
- strong channel: accelerometer + gyroscope engineered features;
- density calibration: StandardScaler -> PCA -> Gaussian class-conditional model;
- binary replay: WALKING_UPSTAIRS vs WALKING_DOWNSTAIRS;
- exploratory extension: all six activities.

The training split is only for fitting sensor-conditioned density approximations; the test split is only for sequential replay.

**Required wording:** "external sequential-sensing replay", not "real-world safety validation".

## 10. Higher-fidelity robotics follow-on — PRISM

PRISM can instantiate a contact-rich replay with robot state, force/torque, tactile and RGB-D modalities. A defensible design is:

- weak channel: robot state + low-risk force/torque summary;
- strong channel: tactile + richer force/torque/RGB-D representation;
- hypothesis: stable/contact mode or task-specific binary regime;
- split by trajectory/task, never random frames across the same trajectory;
- calibrate densities on training trajectories only;
- replay held-out trajectories sequentially.

A passive replay cannot establish that a physical action was safe. A real robot experiment is required for that claim.

## 11. Monte Carlo scale

| Purpose | Trials/config |
|---|---:|
| Smoke/code verification | 3–500 depending on notebook |
| Iteration/default | 300–5,000 |
| Main synthetic paper results | >=10,000 |
| alpha/delta around 1e-4 | preferably >=100,000 or use dedicated rare-event methods |
| Multihypothesis N=10 | choose enough trials to stabilize error and q95 estimates; report CIs |

Do not infer "probability <= 1e-5" from zero events in 10,000 trials.

## 12. Main-paper vs supplement

### Main paper
1. Lower-bound / proposed / oracle figure.
2. First-order convergence figure.
3. PoC surface or regime comparison.
4. Record-envelope = numerical LP verification.
5. False-unlock calibration table/figure.
6. Finite-confidence decomposition.
7. One compact external UCI replay table.

### Supplement
- full five-regime results;
- L=2/3/5/10 stage occupancies;
- 1,000 random LP instances;
- N=3/5/10 multihypothesis results;
- Gaussian/correlation/misspecification stress tests;
- full confidence intervals and seed-level results;
- PRISM follow-on if available.
