from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence
import math

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.stats import norm

EPS = 1e-12


def _clip_prob(x: float) -> float:
    return float(np.clip(x, EPS, 1.0 - EPS))


def kl_bernoulli(p: float, q: float) -> float:
    p = _clip_prob(p)
    q = _clip_prob(q)
    return p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q))


def binary_kl(p: float, q: float) -> float:
    return kl_bernoulli(p, q)


def bernoulli_llr(y: int | np.ndarray, p0: float, p1: float):
    p0 = _clip_prob(p0)
    p1 = _clip_prob(p1)
    y = np.asarray(y)
    return y * math.log(p0 / p1) + (1 - y) * math.log((1 - p0) / (1 - p1))


def record_envelope(K: Sequence[float]) -> np.ndarray:
    K = np.asarray(K, dtype=float)
    if K.ndim != 1 or len(K) == 0:
        raise ValueError('K must be a non-empty one-dimensional sequence.')
    return np.maximum.accumulate(K)


def ladder_lower_bound(K: Sequence[float], d: Sequence[float]) -> float:
    K = np.asarray(K, dtype=float)
    d = np.asarray(d, dtype=float)
    if len(K) != len(d):
        raise ValueError('K and d must have the same length.')
    if np.any(d <= 0):
        raise ValueError('All KL rates d must be positive.')
    if np.any(np.diff(d) < -1e-12):
        raise ValueError('d must be nondecreasing for the closed-form record-envelope bound.')
    kb = record_envelope(K)
    inc = np.diff(np.r_[0.0, kb])
    return float(np.sum(inc / d))


def solve_ladder_lp(K: Sequence[float], d: Sequence[float]) -> tuple[float, np.ndarray]:
    K = np.asarray(K, dtype=float)
    d = np.asarray(d, dtype=float)
    if len(K) != len(d):
        raise ValueError('K and d must have the same length.')
    L = len(K)
    A = np.zeros((L, L), dtype=float)
    for ell in range(L):
        A[ell, : ell + 1] = d[: ell + 1]
    # scipy linprog uses A_ub x <= b_ub, so negate prefix constraints.
    res = linprog(np.ones(L), A_ub=-A, b_ub=-K, bounds=[(0, None)] * L, method='highs')
    if not res.success:
        raise RuntimeError(f'LP failed: {res.message}')
    return float(res.fun), np.asarray(res.x, dtype=float)


def theoretical_c_gate(d: Sequence[float], rhos_with_endpoints: Sequence[float]) -> float:
    d = np.asarray(d, dtype=float)
    r = np.asarray(rhos_with_endpoints, dtype=float)
    if len(r) != len(d) + 1:
        raise ValueError('rhos_with_endpoints must have length len(d)+1 and include 0 and 1.')
    if abs(r[0]) > 1e-12 or abs(r[-1] - 1.0) > 1e-12:
        raise ValueError('rho endpoints must be 0 and 1.')
    if np.any(np.diff(r) < -1e-12):
        raise ValueError('rho sequence must be nondecreasing.')
    return float(np.sum(np.diff(r) / d))


def price_of_certification(d: Sequence[float], rhos_with_endpoints: Sequence[float]) -> float:
    d = np.asarray(d, dtype=float)
    return float(d[-1] * theoretical_c_gate(d, rhos_with_endpoints))


def mean_ci(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float, float]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return math.nan, math.nan, math.nan
    m = float(np.mean(x))
    if len(x) == 1:
        return m, m, m
    z = norm.ppf((1 + confidence) / 2)
    se = float(np.std(x, ddof=1) / math.sqrt(len(x)))
    return m, m - z * se, m + z * se


def wilson_interval(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n <= 0:
        return math.nan, math.nan
    phat = successes / n
    z = norm.ppf((1 + confidence) / 2)
    den = 1 + z*z/n
    center = (phat + z*z/(2*n)) / den
    half = z * math.sqrt((phat*(1-phat)/n) + z*z/(4*n*n)) / den
    return max(0.0, center - half), min(1.0, center + half)


@dataclass(frozen=True)
class BernoulliAction:
    p0: float
    p1: float
    name: str = ''

    @property
    def d0(self) -> float:
        return kl_bernoulli(self.p0, self.p1)

    @property
    def d1(self) -> float:
        return kl_bernoulli(self.p1, self.p0)

    @property
    def c(self) -> float:
        vals = [
            abs(math.log(_clip_prob(self.p0) / _clip_prob(self.p1))),
            abs(math.log((1-_clip_prob(self.p0)) / (1-_clip_prob(self.p1)))),
        ]
        return max(vals)

    def draw(self, rng: np.random.Generator, true_h: int) -> int:
        p = self.p0 if true_h == 0 else self.p1
        return int(rng.random() < p)

    def llr(self, y: int) -> float:
        return float(bernoulli_llr(y, self.p0, self.p1))


def make_alpha_from_rhos(delta: float, rhos: Sequence[float]) -> np.ndarray:
    rhos = np.asarray(rhos, dtype=float)
    return np.power(delta, rhos)


def _thresholds_from_alphas(alphas: Sequence[float], delta: float) -> tuple[np.ndarray, float]:
    alphas = np.asarray(alphas, dtype=float)
    B = np.log(1.0 / alphas) if len(alphas) else np.array([], dtype=float)
    A = math.log(1.0 / delta)
    return B, A


def simulate_binary_ladder(
    actions: Sequence[BernoulliAction],
    alphas: Sequence[float],
    delta: float,
    true_h: int,
    n_trials: int = 1000,
    seed: int = 0,
    max_steps: int = 100000,
    policy: str = 'running_max',
    fixed_unlock_samples: Sequence[int] | None = None,
) -> pd.DataFrame:
    """Simulate binary sequential testing with nested Bernoulli actions.

    Policies:
      running_max: proposed irreversible certificate using max evidence.
      current_evidence: level determined by current S_t; may relock.
      oracle: strongest action from time 0.
      weak_only: always first action.
      fixed: unlock levels after fixed sample-count milestones.
    """
    if true_h not in (0, 1):
        raise ValueError('true_h must be 0 or 1.')
    L = len(actions)
    if len(alphas) != max(0, L - 1):
        raise ValueError('Need L-1 alpha thresholds.')
    B, A = _thresholds_from_alphas(alphas, delta)
    if len(B) and np.any(np.diff(B) <= 0):
        # alphas must decrease so thresholds increase.
        raise ValueError('Certification thresholds must be strictly increasing.')
    if len(B) and not (B[-1] < A + 1e-12):
        raise ValueError('Last certification threshold must be below terminal threshold.')
    if policy == 'fixed':
        if fixed_unlock_samples is None:
            # Reasonable deterministic milestones at the proposed thresholds / d0.
            fixed_unlock_samples = [max(1, int(math.ceil(B[i] / actions[i].d0))) for i in range(L-1)]
        if len(fixed_unlock_samples) != L - 1:
            raise ValueError('fixed_unlock_samples must have L-1 entries.')

    rng = np.random.default_rng(seed)
    rows = []
    for trial in range(n_trials):
        S = 0.0
        M = 0.0
        level = L - 1 if policy == 'oracle' else 0
        stage_counts = np.zeros(L, dtype=int)
        crossed = np.zeros(max(0, L - 1), dtype=bool)
        unlock_times = np.full(max(0, L - 1), np.nan)
        overshoots = np.full(max(0, L - 1), np.nan)
        relocks = 0
        prev_level = level
        decision = -1

        for t in range(1, max_steps + 1):
            if policy == 'oracle':
                level = L - 1
            elif policy == 'weak_only':
                level = 0
            elif policy == 'running_max':
                level = int(np.searchsorted(B, M, side='right')) if len(B) else 0
            elif policy == 'current_evidence':
                level = int(np.searchsorted(B, S, side='right')) if len(B) else 0
                if level < prev_level:
                    relocks += 1
            elif policy == 'fixed':
                level = sum(t - 1 >= n for n in fixed_unlock_samples)
            else:
                raise ValueError(f'Unknown policy {policy}')
            level = min(level, L - 1)
            prev_level = level

            a = actions[level]
            y = a.draw(rng, true_h)
            inc = a.llr(y)
            S += inc
            M = max(M, S)
            stage_counts[level] += 1

            # Record first crossing for every threshold reached by running evidence maximum.
            for k, b in enumerate(B):
                if (not crossed[k]) and M >= b:
                    crossed[k] = True
                    unlock_times[k] = t
                    overshoots[k] = M - b

            if S >= A:
                decision = 0
                break
            if S <= -A:
                decision = 1
                break
        else:
            decision = 0 if S >= 0 else 1

        row = {
            'trial': trial,
            'true_h': true_h,
            'decision': decision,
            'error': int(decision != true_h),
            'tau': int(np.sum(stage_counts)),
            'final_S': S,
            'max_S': M,
            'max_level_reached': int(np.max(np.where(stage_counts > 0)[0])) if np.any(stage_counts > 0) else 0,
            'false_unlock': (int(true_h == 1 and np.any(crossed)) if policy == 'running_max' else
                             int(true_h == 1 and np.sum(stage_counts[1:]) > 0) if policy in ('current_evidence','fixed') else np.nan),
            'all_levels_unlocked': int(np.all(crossed)) if (policy == 'running_max' and len(crossed)) else np.nan,
            'failed_unlock': (int(true_h == 0 and len(crossed) and not np.all(crossed)) if policy == 'running_max' else np.nan),
            'relocks': relocks,
        }
        for ell in range(L):
            row[f'N{ell+1}'] = int(stage_counts[ell])
        for k in range(L - 1):
            row[f'unlock_t{k+1}'] = unlock_times[k]
            row[f'overshoot{k+1}'] = overshoots[k]
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_binary_runs(df: pd.DataFrame) -> dict:
    n = len(df)
    mean_tau, lo_tau, hi_tau = mean_ci(df['tau'])
    err = int(df['error'].sum())
    eu_lo, eu_hi = wilson_interval(err, n)
    fu_series = df['false_unlock'].dropna() if 'false_unlock' in df else pd.Series(dtype=float)
    if len(fu_series):
        false_unlock = int(fu_series.sum())
        fu_lo, fu_hi = wilson_interval(false_unlock, len(fu_series))
        fu_rate = false_unlock / len(fu_series)
    else:
        fu_lo = fu_hi = fu_rate = math.nan
    out = {
        'n_trials': n,
        'mean_tau': mean_tau,
        'mean_tau_ci_lo': lo_tau,
        'mean_tau_ci_hi': hi_tau,
        'median_tau': float(df['tau'].median()),
        'q95_tau': float(df['tau'].quantile(0.95)),
        'error_rate': err / n if n else math.nan,
        'error_ci_lo': eu_lo,
        'error_ci_hi': eu_hi,
        'false_unlock_rate': fu_rate,
        'false_unlock_ci_lo': fu_lo,
        'false_unlock_ci_hi': fu_hi,
        'failed_unlock_rate': float(df['failed_unlock'].dropna().mean()) if ('failed_unlock' in df and df['failed_unlock'].notna().any()) else math.nan,
        'mean_relocks': float(df['relocks'].mean()) if 'relocks' in df else math.nan,
    }
    for c in [c for c in df.columns if c.startswith('N') and c[1:].isdigit()]:
        out[f'mean_{c}'] = float(df[c].mean())
    return out


def finite_confidence_two_level(action_w: BernoulliAction, action_s: BernoulliAction, delta: float, alpha: float, beta: float):
    Kc = binary_kl(1-beta, alpha)
    Kf = binary_kl(1-delta, delta)
    dw, ds = action_w.d0, action_s.d0
    Ld = Kc/dw + max(0.0, Kf-Kc)/ds
    Bc = math.log(1/alpha)
    A = math.log(1/delta)
    Uthr = Bc/dw + max(0.0, A-Bc)/ds
    Ubd = Uthr + action_w.c/dw + action_s.c/ds
    return {
        'Kc': Kc, 'Kf': Kf, 'L_delta': Ld, 'U_thr': Uthr, 'U_bd': Ubd,
        'boundary_factor': Uthr/Ld,
        'overshoot_factor': Ubd/Uthr,
        'total_factor': Ubd/Ld,
    }


def multihyp_stop_condition(pairwise_llr: np.ndarray, threshold: float) -> tuple[bool, int | None]:
    pairwise_llr = np.asarray(pairwise_llr, dtype=float)
    N = pairwise_llr.shape[0]
    for i in range(N):
        vals = [pairwise_llr[i, j] for j in range(N) if j != i]
        if min(vals) >= threshold:
            return True, i
    return False, None


def pairwise_llr_from_scores(scores: Sequence[float]) -> np.ndarray:
    s = np.asarray(scores, dtype=float)
    return s[:, None] - s[None, :]


def bernoulli_logpmf(y: int, p: float) -> float:
    p = _clip_prob(p)
    return math.log(p if y else 1-p)


def generate_multihyp_bernoulli_probs(N: int, mode: str = 'uniform_hardest') -> np.ndarray:
    """Return shape (N, 2): weak and strong Bernoulli parameters."""
    if N < 3:
        raise ValueError('Use N>=3 for multihypothesis benchmarks.')
    if mode == 'uniform_hardest':
        # H0 at one edge; H1 is nearest under both actions.
        weak = np.linspace(0.15, 0.85, N)
        strong = np.linspace(0.05, 0.95, N)
    elif mode == 'switching':
        weak = np.linspace(0.08, 0.92, N)
        strong = np.linspace(0.92, 0.08, N)
        weak[0], strong[0] = 0.50, 0.50
        weak[1], strong[1] = 0.58, 0.90   # hardest at weak
        weak[2], strong[2] = 0.10, 0.58   # hardest at strong
        if N > 3:
            vals = np.linspace(0.15, 0.85, N-3)
            weak[3:] = vals
            strong[3:] = vals[::-1]
    else:
        raise ValueError('mode must be uniform_hardest or switching.')
    return np.column_stack([np.clip(weak, 0.02, 0.98), np.clip(strong, 0.02, 0.98)])


def simulate_multihypothesis_gate(
    probs: np.ndarray,
    true_h: int,
    delta: float = 0.05,
    alpha: float = 0.05,
    n_trials: int = 500,
    seed: int = 0,
    policy: str = 'gated',
    max_steps: int = 50000,
) -> pd.DataFrame:
    """Exploratory known-simple multihypothesis gate.

    probs[h, a] is Bernoulli parameter for hypothesis h and action a.
    Action 0 = weak; action 1 = strong. Strong unlocks when H0 beats every
    alternative by B=log(1/alpha). Final stopping uses pairwise margin
    A=log((N-1)/delta), giving a simple union-bound-valid multiway rule.

    This is an empirical extension; it is not a matched theorem from the paper.
    """
    probs = np.asarray(probs, dtype=float)
    N, Acount = probs.shape
    if Acount != 2:
        raise ValueError('This benchmark currently uses exactly two actions.')
    if not (0 <= true_h < N):
        raise ValueError('Invalid true_h.')
    B = math.log(1/alpha)
    Astop = math.log((N-1)/delta)
    rng = np.random.default_rng(seed)
    rows=[]
    for tr in range(n_trials):
        scores=np.zeros(N)
        unlocked = policy == 'oracle'
        unlock_t=np.nan
        nweak=nstrong=0
        decision=None
        for t in range(1, max_steps+1):
            action = 1 if (unlocked and policy != 'weak_only') or policy == 'oracle' else 0
            ptrue = probs[true_h, action]
            y = int(rng.random() < ptrue)
            for h in range(N):
                scores[h] += bernoulli_logpmf(y, probs[h, action])
            if action == 0: nweak += 1
            else: nstrong += 1
            pair = pairwise_llr_from_scores(scores)
            if policy == 'gated' and not unlocked:
                # Certification that H0 dominates every alternative.
                if min(pair[0, j] for j in range(1, N)) >= B:
                    unlocked=True
                    unlock_t=t
            stopped, hhat = multihyp_stop_condition(pair, Astop)
            if stopped:
                decision=hhat
                break
        if decision is None:
            decision=int(np.argmax(scores))
        rows.append({
            'trial':tr,'true_h':true_h,'decision':decision,
            'error':int(decision!=true_h),'tau':nweak+nstrong,
            'Nweak':nweak,'Nstrong':nstrong,'unlocked':int(unlocked),
            'false_unlock':int(true_h!=0 and unlocked),'unlock_t':unlock_t,
        })
    return pd.DataFrame(rows)


def gaussian_llr(y: float, mu0: float, mu1: float, sigma: float = 1.0) -> float:
    # Equal-variance Gaussian log likelihood ratio log f0/f1.
    return ((y-mu1)**2 - (y-mu0)**2) / (2*sigma*sigma)


def gaussian_kl(mu0: float, mu1: float, sigma: float = 1.0) -> float:
    return (mu0-mu1)**2 / (2*sigma*sigma)


def simulate_gaussian_binary(
    means_true: Sequence[tuple[float,float]],
    means_model: Sequence[tuple[float,float]] | None,
    sigma: float,
    alphas: Sequence[float],
    delta: float,
    true_h: int,
    n_trials: int = 1000,
    seed: int = 0,
    corr: float = 0.0,
    max_steps: int = 100000,
) -> pd.DataFrame:
    """Gaussian stress-test version of the binary ladder.

    `corr>0` introduces AR(1) noise while the likelihood still assumes iid data,
    intentionally testing robustness outside the theorem assumptions.
    """
    mt = np.asarray(means_true, dtype=float)
    mm = mt.copy() if means_model is None else np.asarray(means_model, dtype=float)
    L = len(mt)
    B,A = _thresholds_from_alphas(alphas, delta)
    rng=np.random.default_rng(seed)
    rows=[]
    for tr in range(n_trials):
        S=M=0.0
        zprev=0.0
        stage_counts=np.zeros(L,dtype=int)
        crossed=np.zeros(L-1,dtype=bool)
        overs=np.full(L-1,np.nan)
        dec=None
        for t in range(1,max_steps+1):
            level=int(np.searchsorted(B,M,side='right')) if len(B) else 0
            level=min(level,L-1)
            eps=rng.normal()
            z = corr*zprev + math.sqrt(max(0.0,1-corr*corr))*eps
            zprev=z
            mu_true=mt[level, true_h]
            y=mu_true + sigma*z
            mu0,mu1=mm[level]
            S += gaussian_llr(y,mu0,mu1,sigma)
            M=max(M,S)
            stage_counts[level]+=1
            for k,b in enumerate(B):
                if not crossed[k] and M>=b:
                    crossed[k]=True; overs[k]=M-b
            if S>=A: dec=0; break
            if S<=-A: dec=1; break
        if dec is None: dec=0 if S>=0 else 1
        row={'trial':tr,'true_h':true_h,'decision':dec,'error':int(dec!=true_h),
             'tau':int(stage_counts.sum()),'false_unlock':int(true_h==1 and crossed.any()),
             'failed_unlock':int(true_h==0 and len(crossed) and not crossed.all()),
             'final_S':S,'max_S':M}
        for l in range(L): row[f'N{l+1}']=int(stage_counts[l])
        for k in range(L-1): row[f'overshoot{k+1}']=overs[k]
        rows.append(row)
    return pd.DataFrame(rows)
