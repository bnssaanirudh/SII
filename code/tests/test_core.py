import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from gated_benchmarks import (
    kl_bernoulli,
    record_envelope,
    ladder_lower_bound,
    solve_ladder_lp,
    theoretical_c_gate,
    price_of_certification,
    bernoulli_llr,
    wilson_interval,
    multihyp_stop_condition,
)


def test_bernoulli_kl_matches_known_paper_values():
    assert abs(kl_bernoulli(0.7, 0.5) - 0.0822828785) < 1e-8
    assert abs(kl_bernoulli(0.8, 0.2) - 0.8317766167) < 1e-8


def test_record_envelope_handles_nonmonotone_requirements():
    K = np.array([1.9942, 1.5369, 4.5032])
    got = record_envelope(K)
    np.testing.assert_allclose(got, [1.9942, 1.9942, 4.5032])


def test_closed_form_matches_numeric_lp_nonmonotone():
    K = np.array([1.9942, 1.5369, 4.5032])
    d = np.array([0.10, 0.40, 1.00])
    closed = ladder_lower_bound(K, d)
    numeric, x = solve_ladder_lp(K, d)
    assert abs(closed - 22.4512) < 2e-4
    assert abs(closed - numeric) < 1e-8
    assert np.all(x >= -1e-10)


def test_asymptotic_constant_and_poc_two_level():
    d = np.array([0.1, 1.0])
    rhos = np.array([0.0, 0.4, 1.0])
    c = theoretical_c_gate(d, rhos)
    assert abs(c - (0.4/0.1 + 0.6/1.0)) < 1e-12
    poc = price_of_certification(d, rhos)
    assert abs(poc - 4.6) < 1e-12


def test_bernoulli_llr_signs_are_correct():
    # Under H0 with p0>p1, y=1 should support H0.
    assert bernoulli_llr(1, 0.7, 0.5) > 0
    # y=0 should support H1 for this pair.
    assert bernoulli_llr(0, 0.7, 0.5) < 0


def test_wilson_interval_contains_observed_rate():
    lo, hi = wilson_interval(5, 100)
    assert lo <= 0.05 <= hi
    assert 0 <= lo <= hi <= 1


def test_multihyp_stop_requires_all_pairwise_margins():
    pairwise = np.array([
        [0.0, 5.0, 6.0],
        [-5.0, 0.0, 1.0],
        [-6.0, -1.0, 0.0],
    ])
    stopped, h = multihyp_stop_condition(pairwise, threshold=4.0)
    assert stopped and h == 0
    stopped2, _ = multihyp_stop_condition(pairwise, threshold=5.5)
    assert not stopped2


def test_summary_preserves_not_applicable_false_unlock_as_nan():
    import pandas as pd
    df = pd.DataFrame({
        'tau':[1,2], 'error':[0,0], 'false_unlock':[np.nan,np.nan],
        'failed_unlock':[np.nan,np.nan], 'relocks':[0,0], 'N1':[1,2]
    })
    s = __import__('gated_benchmarks').summarize_binary_runs(df)
    assert np.isnan(s['false_unlock_rate'])
    assert np.isnan(s['failed_unlock_rate'])
