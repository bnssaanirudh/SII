# PRISM Robotics Replay Protocol (Optional Extension)

Use this only if a higher-fidelity robotics external study is desired after the UCI replay.

## Objective
Instantiate the same evidence-gated sensing logic on contact-rich robot trajectories while avoiding a false claim of physical safety validation.

## Suggested hierarchy

**Weak channel:** robot state + low-risk force/torque summaries.

**Strong channel:** tactile + richer force/torque + optional RGB-D embedding.

## Hypotheses
Prefer one clearly defined binary regime (e.g., stable vs unstable contact) before attempting multiple task labels. The labels must be derivable independently of the gated algorithm.

## Data splitting
Split at trajectory/task level, not frame level. All calibration, PCA/representation fitting, density fitting, and threshold selection use training/validation trajectories only. Held-out trajectories are replayed exactly once for reporting.

## Sequential replay
At each replay step:

1. use weak-channel log likelihoods while uncertified;
2. update cumulative evidence and running maximum;
3. unlock richer modality after the certification boundary;
4. continue until the terminal decision boundary;
5. record time-to-decision, modality use, error and false unlock.

## Required caveat
Offline replay shows whether richer sensing can be *scheduled* by a statistical certificate. It does not establish that commanding a physically stronger action after that certificate is safe. That requires an intervention study on the robot with an independently justified safety envelope.
