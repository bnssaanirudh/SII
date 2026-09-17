from pathlib import Path
import nbformat as nbf

ROOT = Path('/mnt/data/gated_certification_benchmarks')
NB = ROOT/'notebooks'
NB.mkdir(exist_ok=True)


def common_setup(title, scope):
    return [
        nbf.v4.new_markdown_cell(f"# {title}\n\n{scope}\n\n**Execution modes:** `SMOKE_TEST=1` performs a small offline code-path check; default settings run a moderate benchmark; `FULL_RUN=1` enables publication-scale Monte Carlo. Smoke outputs are verification-only and must not be reported as experimental results."),
        nbf.v4.new_code_cell("""from pathlib import Path
import os, sys, math, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path.cwd().resolve()
ROOT = HERE.parent if HERE.name == 'notebooks' else HERE
if not (ROOT/'src'/'gated_benchmarks.py').exists():
    for cand in [HERE, *HERE.parents]:
        if (cand/'src'/'gated_benchmarks.py').exists():
            ROOT = cand; break
sys.path.insert(0, str(ROOT/'src'))
( ROOT/'results').mkdir(exist_ok=True)
( ROOT/'figures').mkdir(exist_ok=True)
FULL_RUN = os.getenv('FULL_RUN','0') == '1'
SMOKE_TEST = os.getenv('SMOKE_TEST','0') == '1'
print('ROOT =', ROOT)
print('FULL_RUN =', FULL_RUN, 'SMOKE_TEST =', SMOKE_TEST)
"""),
    ]

# Notebook 1
cells = common_setup(
    '01 — Binary Theory Benchmarks',
    'Theorem-aligned Bernoulli experiments: lower-bound comparison, first-order convergence, Price of Certification, false-unlock control, final decision error, baselines, and finite-confidence overshoot.'
)
cells += [
nbf.v4.new_code_cell("""from gated_benchmarks import *

weak = BernoulliAction(0.7, 0.5, 'weak')
strong = BernoulliAction(0.8, 0.2, 'strong')
actions = [weak, strong]
print('d_w =', weak.d0, 'd_s =', strong.d0)
print('increment bounds =', weak.c, strong.c)
"""),
nbf.v4.new_markdown_cell("## 1. Main benchmark: lower bound vs proposed vs oracle/baselines"),
nbf.v4.new_code_cell("""deltas = [1e-1, 5e-2, 1e-2, 1e-3] if not FULL_RUN else [1e-1,5e-2,1e-2,1e-3,1e-4,1e-5]
rho = 0.4
n_trials = 300 if SMOKE_TEST else (2500 if not FULL_RUN else 10000)
policies = ['running_max','oracle','weak_only','fixed','current_evidence']
rows=[]
for delta in deltas:
    alpha = delta**rho
    beta = delta
    Kc = binary_kl(1-beta, alpha)
    Kf = binary_kl(1-delta, delta)
    LB = Kc/weak.d0 + max(0,Kf-Kc)/strong.d0
    for pol in policies:
        for h in [0,1]:
            df = simulate_binary_ladder(actions,[alpha],delta,h,n_trials=n_trials,seed=1000+int(1e6*delta)+10*h+policies.index(pol),policy=pol)
            s = summarize_binary_runs(df)
            rows.append({'delta':delta,'alpha':alpha,'rho':rho,'policy':pol,'true_h':h,'LB_H0':LB,**s})
main = pd.DataFrame(rows)
main.to_csv(ROOT/'results'/'binary_main_benchmark.csv',index=False)
main.head()
"""),
nbf.v4.new_code_cell("""tab = main[(main.true_h==0)][['delta','policy','mean_tau','mean_tau_ci_lo','mean_tau_ci_hi','error_rate','false_unlock_rate','LB_H0']].copy()
tab['gap_to_LB']=tab['mean_tau']/tab['LB_H0']
display(tab)
"""),
nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(7,4.5))
for pol in ['running_max','oracle','weak_only']:
    q=main[(main.true_h==0)&(main.policy==pol)].sort_values('delta',ascending=False)
    ax.plot(np.log(1/q.delta),q.mean_tau,marker='o',label=pol)
q=main[(main.true_h==0)&(main.policy=='running_max')].sort_values('delta',ascending=False)
ax.plot(np.log(1/q.delta),q.LB_H0,linestyle='--',label='information lower bound')
ax.set_xlabel('log(1/delta)'); ax.set_ylabel('mean stopping time'); ax.legend(); ax.set_title('Sample complexity vs confidence')
fig.tight_layout(); fig.savefig(ROOT/'figures'/'binary_sample_complexity.png',dpi=180)
plt.show()
"""),
nbf.v4.new_markdown_cell("## 2. First-order optimality diagnostic"),
nbf.v4.new_code_cell("""rhos=np.array([0.0,rho,1.0]); d=np.array([weak.d0,strong.d0])
Cgate=theoretical_c_gate(d,rhos); Coracle=1/strong.d0
q=main[(main.true_h==0)&(main.policy=='running_max')].sort_values('delta',ascending=False).copy()
q['normalized']=q.mean_tau/np.log(1/q.delta)
display(q[['delta','normalized']])
print('C_gate =',Cgate,'C_oracle =',Coracle)
fig,ax=plt.subplots(figsize=(7,4.5)); ax.plot(np.log(1/q.delta),q.normalized,marker='o',label='empirical gated')
ax.axhline(Cgate,linestyle='--',label='C_gate'); ax.axhline(Coracle,linestyle=':',label='C_oracle')
ax.set_xlabel('log(1/delta)'); ax.set_ylabel('E[tau]/log(1/delta)'); ax.legend(); ax.set_title('First-order convergence')
fig.tight_layout(); fig.savefig(ROOT/'figures'/'binary_first_order.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell("## 3. Price of Certification surface"),
nbf.v4.new_code_cell("""ratios=np.array([1,2,5,10,20,50],dtype=float)
rho_grid=np.arange(.1,1.0,.1)
P=np.array([[1+r*(g-1) for g in ratios] for r in rho_grid])
fig,ax=plt.subplots(figsize=(7.5,4.8)); im=ax.imshow(P,aspect='auto',origin='lower')
ax.set_xticks(range(len(ratios)),ratios); ax.set_yticks(range(len(rho_grid)),[f'{x:.1f}' for x in rho_grid])
ax.set_xlabel('d_s/d_w'); ax.set_ylabel('rho'); ax.set_title('Theoretical Price of Certification')
fig.colorbar(im,ax=ax,label='PoC'); fig.tight_layout(); fig.savefig(ROOT/'figures'/'poc_surface.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell("## 4. Empirical Price of Certification across difficulty regimes"),
nbf.v4.new_code_cell("""regimes={
    'easy':(.80,.20,.95,.05),
    'moderate':(.70,.50,.80,.20),
    'hard':(.60,.50,.70,.30),
    'very_hard':(.55,.50,.65,.35),
    'large_gap':(.70,.50,.99,.01),
}
delta_reg=.01; alpha_reg=delta_reg**rho
nreg=60 if SMOKE_TEST else (800 if not FULL_RUN else 5000)
reg_rows=[]
for name,(p0w,p1w,p0s,p1s) in regimes.items():
    w=BernoulliAction(p0w,p1w,'weak'); s=BernoulliAction(p0s,p1s,'strong')
    if s.d0 < w.d0:
        raise ValueError(f'{name}: strong action must have at least as much H0 KL as weak action')
    dvec=np.array([w.d0,s.d0]); rvec=np.array([0.,rho,1.])
    poc_th=price_of_certification(dvec,rvec)
    prop=simulate_binary_ladder([w,s],[alpha_reg],delta_reg,0,n_trials=nreg,seed=1200+len(reg_rows),policy='running_max')
    ora=simulate_binary_ladder([w,s],[alpha_reg],delta_reg,0,n_trials=nreg,seed=2200+len(reg_rows),policy='oracle')
    reg_rows.append({'regime':name,'d_w':w.d0,'d_s':s.d0,'d_ratio':s.d0/w.d0,
                     'theoretical_PoC':poc_th,'empirical_PoC':prop.tau.mean()/ora.tau.mean(),
                     'gated_mean_tau':prop.tau.mean(),'oracle_mean_tau':ora.tau.mean(),
                     'gated_error':prop.error.mean(),'oracle_error':ora.error.mean()})
regimes_df=pd.DataFrame(reg_rows); display(regimes_df)
regimes_df.to_csv(ROOT/'results'/'difficulty_regimes_poc.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4.5)); x=np.arange(len(regimes_df)); ax.plot(x,regimes_df.theoretical_PoC,marker='o',label='theoretical first-order PoC'); ax.plot(x,regimes_df.empirical_PoC,marker='s',label='empirical stopping-time ratio'); ax.set_xticks(x,regimes_df.regime,rotation=25); ax.set_ylabel('Price of certification'); ax.legend(); ax.set_title('Theory vs empirical certification cost'); fig.tight_layout(); fig.savefig(ROOT/'figures'/'empirical_poc_regimes.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell("## 5. Anytime false-unlock calibration and terminal error"),
nbf.v4.new_code_cell("""alphas=[.1,.05,.01,.005,.001] if FULL_RUN else [.1,.05,.01]
cal=[]
for alpha in alphas:
    # choose delta below alpha so B < A
    delta=min(alpha/10,1e-3)
    n=500 if SMOKE_TEST else (5000 if not FULL_RUN else (50000 if alpha>=.01 else 100000))
    d1=simulate_binary_ladder(actions,[alpha],delta,1,n_trials=n,seed=33+int(alpha*1e6),policy='running_max')
    s1=summarize_binary_runs(d1)
    d0=simulate_binary_ladder(actions,[alpha],delta,0,n_trials=n,seed=77+int(alpha*1e6),policy='running_max')
    s0=summarize_binary_runs(d0)
    cal.append({'alpha_target':alpha,'delta':delta,'n':n,'false_unlock':s1['false_unlock_rate'],
                'fu_lo':s1['false_unlock_ci_lo'],'fu_hi':s1['false_unlock_ci_hi'],
                'err_H0':s0['error_rate'],'err_H1':s1['error_rate']})
cal=pd.DataFrame(cal); cal.to_csv(ROOT/'results'/'false_unlock_calibration.csv',index=False); display(cal)
"""),
nbf.v4.new_markdown_cell("## 6. Finite-confidence decomposition and empirical overshoot"),
nbf.v4.new_code_cell("""fin=[]
for delta in deltas:
    alpha=delta**rho; beta=delta
    theory=finite_confidence_two_level(weak,strong,delta,alpha,beta)
    df=simulate_binary_ladder(actions,[alpha],delta,0,n_trials=n_trials,seed=909+int(delta*1e6),policy='running_max')
    ovs=df['overshoot1'].dropna()
    fin.append({'delta':delta,'alpha':alpha,'emp_mean_tau':df.tau.mean(),'mean_overshoot':ovs.mean(),
                'q95_overshoot':ovs.quantile(.95) if len(ovs) else np.nan,**theory})
fin=pd.DataFrame(fin); fin.to_csv(ROOT/'results'/'finite_confidence.csv',index=False); display(fin)
"""),
nbf.v4.new_markdown_cell("### Interpretation guardrail\nThe Bernoulli experiments above are **theorem validation** because the action-conditioned laws are known, observations are conditionally independent, and log-likelihood increments are bounded. The empirical curves should be discussed as finite-sample checks of the proved predictions, not as replacements for the proofs."),
]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
nbf.write(nb,NB/'01_binary_theory_benchmarks.ipynb')

# Notebook 2
cells=common_setup('02 — Record Envelope, LP, and Ladder Scaling','Validates the non-monotone running-max envelope structurally and numerically, then tests ladder depth.')
cells += [
nbf.v4.new_code_cell("""from gated_benchmarks import *
from scipy.optimize import linprog
"""),
nbf.v4.new_markdown_cell('## 1. Paper counterexample and other non-monotone patterns'),
nbf.v4.new_code_cell("""patterns=[
    (np.array([1.9942,1.5369,4.5032]),np.array([.10,.40,1.00]),'paper example'),
    (np.array([1.,4.,2.,5.]),np.array([.08,.15,.4,1.]),'alternating'),
    (np.array([3.,1.,1.5,7.,5.,8.]),np.array([.05,.1,.2,.4,.7,1.]),'deep nonmonotone')]
rows=[]
for K,d,name in patterns:
    closed=ladder_lower_bound(K,d); numeric,x=solve_ladder_lp(K,d)
    rows.append({'name':name,'closed_form':closed,'numeric_lp':numeric,'abs_diff':abs(closed-numeric),'K':K.tolist(),'Kbar':record_envelope(K).tolist(),'Xstar':x.tolist()})
pat=pd.DataFrame(rows); display(pat); pat.to_json(ROOT/'results'/'record_envelope_examples.json',orient='records',indent=2)
"""),
nbf.v4.new_markdown_cell('## 2. Random LP verification — 1,000 instances in full mode'),
nbf.v4.new_code_cell("""rng=np.random.default_rng(42); reps=50 if SMOKE_TEST else (300 if not FULL_RUN else 1000); out=[]
for r in range(reps):
    L=int(rng.integers(2,11)); d=np.sort(rng.uniform(.03,2.0,L)); K=rng.uniform(.1,8.0,L)
    closed=ladder_lower_bound(K,d); num,x=solve_ladder_lp(K,d)
    out.append({'rep':r,'L':L,'closed':closed,'numeric':num,'abs_diff':abs(closed-num),'max_K_drop':float(np.max(np.maximum(0,-np.diff(K)))) if L>1 else 0})
rnd=pd.DataFrame(out); display(rnd.describe()); print('max abs error=',rnd.abs_diff.max())
rnd.to_csv(ROOT/'results'/'random_lp_verification.csv',index=False)
assert rnd.abs_diff.max() < 1e-7
"""),
nbf.v4.new_code_cell("""fig,ax=plt.subplots(figsize=(6,4.5)); ax.scatter(rnd.numeric,rnd.closed,s=12); lo=min(rnd.numeric.min(),rnd.closed.min()); hi=max(rnd.numeric.max(),rnd.closed.max()); ax.plot([lo,hi],[lo,hi],linestyle='--'); ax.set_xlabel('Numerical LP optimum'); ax.set_ylabel('Record-envelope closed form'); ax.set_title('Closed form = LP optimum'); fig.tight_layout(); fig.savefig(ROOT/'figures'/'lp_verification.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell('## 3. Ladder-depth scaling'),
nbf.v4.new_code_cell("""depth_rows=[]
for L in [2,3,5,10]:
    d=np.geomspace(.05,1.0,L); r=np.linspace(0,1,L+1); c=theoretical_c_gate(d,r); poc=price_of_certification(d,r)
    depth_rows.append({'L':L,'C_gate':c,'PoC':poc,'d1':d[0],'dL':d[-1]})
depth=pd.DataFrame(depth_rows); display(depth); depth.to_csv(ROOT/'results'/'ladder_depth_scaling.csv',index=False)
fig,ax=plt.subplots(figsize=(6,4)); ax.plot(depth.L,depth.PoC,marker='o'); ax.set_xlabel('Number of levels L'); ax.set_ylabel('PoC'); ax.set_title('Certification depth with geometric information rates'); fig.tight_layout(); fig.savefig(ROOT/'figures'/'ladder_depth.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell('## 4. Sequential multi-level validation (L=2,3,5,10)'),
nbf.v4.new_code_cell("""seq_rows=[]
delta_seq=.02
nseq=30 if SMOKE_TEST else (300 if not FULL_RUN else 2000)
for L in [2,3,5,10]:
    # Bernoulli actions with progressively larger KL against H1=Bernoulli(.5).
    p0s=np.linspace(.58,.90,L)
    acts=[BernoulliAction(float(p0),.50,f'level_{i+1}') for i,p0 in enumerate(p0s)]
    dvec=np.array([a.d0 for a in acts])
    rho_pts=np.linspace(0,1,L+1)
    alphas=(delta_seq**rho_pts[1:L]).tolist()
    C=theoretical_c_gate(dvec,rho_pts)
    df=simulate_binary_ladder(acts,alphas,delta_seq,0,n_trials=nseq,seed=500+L,policy='running_max',max_steps=100000)
    sm=summarize_binary_runs(df)
    seq_rows.append({'L':L,'delta':delta_seq,'C_gate':C,'emp_norm_tau':sm['mean_tau']/math.log(1/delta_seq),
                     'mean_tau':sm['mean_tau'],'error_rate':sm['error_rate'],
                     'failed_unlock_rate':sm['failed_unlock_rate'],'PoC_theory':price_of_certification(dvec,rho_pts),
                     'd1':dvec[0],'dL':dvec[-1]})
seq_depth=pd.DataFrame(seq_rows); display(seq_depth)
seq_depth.to_csv(ROOT/'results'/'ladder_depth_empirical.csv',index=False)
fig,ax=plt.subplots(figsize=(6.5,4.3)); ax.plot(seq_depth.L,seq_depth.C_gate,marker='o',label='theoretical C_gate'); ax.plot(seq_depth.L,seq_depth.emp_norm_tau,marker='s',label='empirical E[tau]/log(1/delta)'); ax.set_xlabel('Number of levels L'); ax.set_ylabel('Normalized sample complexity'); ax.set_title('Multi-level sequential validation'); ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'figures'/'ladder_depth_empirical.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell('## 5. Epistemic-trap numerical illustration'),
nbf.v4.new_code_cell("""# Weak action has KL=0; adding epsilon separation makes certification finite but expensive.
eps=[0,.005,.01,.02,.05,.1]; rows=[]
for e in eps:
    p0=.5+e; p1=.5
    d=0.0 if e==0 else kl_bernoulli(p0,p1)
    approx=np.inf if d==0 else math.log(1/.05)/d
    rows.append({'epsilon':e,'weak_KL':d,'approx_samples_to_certificate':approx})
trap=pd.DataFrame(rows); display(trap); trap.to_csv(ROOT/'results'/'trap_scaling.csv',index=False)
"""),
]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}}); nbf.write(nb,NB/'02_record_envelope_lp_ladders.ipynb')

# Notebook 3
cells=common_setup('03 — Multihypothesis Extension Benchmarks','Exploratory extension to N=3,5,10 known simple hypotheses. It tests the appendix intuition and hard-alternative switching, but does not claim the binary matched theorem extends unchanged.')
cells += [
nbf.v4.new_code_cell("""from gated_benchmarks import *
"""),
nbf.v4.new_markdown_cell('## 1. Inspect uniformly-hardest and switching constructions'),
nbf.v4.new_code_cell("""def closest_to_h0(probs, action):
    vals=[]
    for j in range(1,len(probs)):
        vals.append((j,kl_bernoulli(probs[0,action],probs[j,action])))
    return min(vals,key=lambda z:z[1]), vals
for N in [3,5,10]:
    for mode in ['uniform_hardest','switching']:
        p=generate_multihyp_bernoulli_probs(N,mode)
        print()
        print('N=',N,'mode=',mode,'weak closest=',closest_to_h0(p,0)[0],'strong closest=',closest_to_h0(p,1)[0])
        print(p)
"""),
nbf.v4.new_markdown_cell('## 2. Sequential multiway benchmark'),
nbf.v4.new_code_cell("""Ns=[3,5,10]; modes=['uniform_hardest','switching']; policies=['gated','oracle','weak_only']; delta=.05; alpha=.05
n_trials=5 if SMOKE_TEST else (60 if not FULL_RUN else 500)
rows=[]
for N in Ns:
    for mode in modes:
        probs=generate_multihyp_bernoulli_probs(N,mode)
        # H0 tests the gated path; H1 and H2 test false unlocking and alternative discrimination.
        hs=list(range(min(N,3)))
        for h in hs:
            for pol in policies:
                df=simulate_multihypothesis_gate(probs,h,delta=delta,alpha=alpha,n_trials=n_trials,seed=100*N+10*h+policies.index(pol),policy=pol,max_steps=(3000 if SMOKE_TEST else 10000))
                rows.append({'N':N,'mode':mode,'true_h':h,'policy':pol,'mean_tau':df.tau.mean(),'median_tau':df.tau.median(),'q95_tau':df.tau.quantile(.95),'error_rate':df.error.mean(),'false_unlock':df.false_unlock.mean(),'mean_Nweak':df.Nweak.mean(),'mean_Nstrong':df.Nstrong.mean()})
res=pd.DataFrame(rows); display(res); res.to_csv(ROOT/'results'/'multihypothesis_benchmark.csv',index=False)
"""),
nbf.v4.new_code_cell("""q=res[(res.true_h==0)&(res.policy=='gated')]
fig,ax=plt.subplots(figsize=(7,4.5))
for mode in modes:
    z=q[q['mode']==mode]; ax.plot(z.N,z.mean_tau,marker='o',label=mode)
ax.set_xlabel('Number of hypotheses'); ax.set_ylabel('Mean stopping time'); ax.set_title('Exploratory multi-hypothesis scaling'); ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'figures'/'multihypothesis_scaling.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell("## 3. What this adds to the paper\n- `uniform_hardest` numerically checks the appendix regime where one alternative remains hardest across actions.\n- `switching` deliberately violates that simplifying condition: the closest alternative changes between weak and strong actions.\n- The experiment reports how a pairwise-LLR gated rule behaves, but **does not claim matching optimality** in this general setting. A strong result here would motivate a future theorem rather than silently expanding the current theorem."),
]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}}); nbf.write(nb,NB/'03_multihypothesis_extension.ipynb')

# Notebook 4
cells=common_setup('04 — Robustness and Out-of-Assumption Stress Tests','Gaussian increments, AR(1) dependence, model misspecification, and overshoot. These are robustness diagnostics outside parts of the current finite-confidence theory.')
cells += [
nbf.v4.new_code_cell("""from gated_benchmarks import *
means=[(0.0,0.35),(0.0,1.2)]  # (mu0,mu1) per level; evidence under H0 is positive with LLR log f0/f1
sigma=1.0; delta=.01; alpha=.05
print('Gaussian KLs:',[gaussian_kl(a,b,sigma) for a,b in means])
"""),
nbf.v4.new_markdown_cell('## 1. Gaussian iid stress test'),
nbf.v4.new_code_cell("""n=200 if SMOKE_TEST else (2000 if not FULL_RUN else 10000)
rows=[]
for h in [0,1]:
    df=simulate_gaussian_binary(means,None,sigma,[alpha],delta,h,n_trials=n,seed=10+h,corr=0)
    s=summarize_binary_runs(df); rows.append({'setting':'iid Gaussian','true_h':h,**s})
g=pd.DataFrame(rows); display(g)
"""),
nbf.v4.new_markdown_cell('## 2. Dependence stress test: AR(1) correlation'),
nbf.v4.new_code_cell("""rows=[]
for corr in [0,.1,.3,.5,.8]:
    for h in [0,1]:
        df=simulate_gaussian_binary(means,None,sigma,[alpha],delta,h,n_trials=n,seed=100+int(100*corr)+h,corr=corr)
        s=summarize_binary_runs(df); rows.append({'corr':corr,'true_h':h,**s})
corr_df=pd.DataFrame(rows); corr_df.to_csv(ROOT/'results'/'correlation_stress.csv',index=False); display(corr_df[['corr','true_h','mean_tau','error_rate','false_unlock_rate']])
"""),
nbf.v4.new_code_cell("""fig,ax=plt.subplots(figsize=(7,4.5)); q=corr_df[corr_df.true_h==1]; ax.plot(q['corr'],q.error_rate,marker='o',label='terminal error H1'); ax.plot(q['corr'],q.false_unlock_rate,marker='s',label='false unlock H1'); ax.axhline(delta,linestyle='--',label='delta target'); ax.axhline(alpha,linestyle=':',label='alpha target'); ax.set_xlabel('AR(1) correlation'); ax.set_ylabel('Empirical probability'); ax.legend(); ax.set_title('Robustness outside iid assumption'); fig.tight_layout(); fig.savefig(ROOT/'figures'/'correlation_stress.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell('## 3. Model misspecification'),
nbf.v4.new_code_cell("""rows=[]
for eps in [0,.01,.05,.10]:
    # Algorithm uses a shifted H1 model while data come from the original means.
    model=[(means[0][0],means[0][1]+eps),(means[1][0],means[1][1]+eps)]
    for h in [0,1]:
        df=simulate_gaussian_binary(means,model,sigma,[alpha],delta,h,n_trials=n,seed=300+int(eps*1000)+h,corr=0)
        s=summarize_binary_runs(df); rows.append({'misspec':eps,'true_h':h,**s})
mis=pd.DataFrame(rows); mis.to_csv(ROOT/'results'/'misspecification_stress.csv',index=False); display(mis[['misspec','true_h','mean_tau','error_rate','false_unlock_rate']])
"""),
nbf.v4.new_markdown_cell('## 4. Overshoot distributions'),
nbf.v4.new_code_cell("""df=simulate_gaussian_binary(means,None,sigma,[alpha],delta,0,n_trials=n,seed=444,corr=0); ov=df.overshoot1.dropna(); print(ov.describe(percentiles=[.5,.9,.95,.99]));
fig,ax=plt.subplots(figsize=(7,4)); ax.hist(ov,bins=30); ax.set_xlabel('Certification overshoot'); ax.set_ylabel('Count'); ax.set_title('Gaussian threshold overshoot (stress test)'); fig.tight_layout(); fig.savefig(ROOT/'figures'/'gaussian_overshoot.png',dpi=180); plt.show()
"""),
nbf.v4.new_markdown_cell('### Reporting rule\nThese experiments should appear under **Robustness beyond the formal assumptions**. Correlation and model misspecification intentionally violate the theorem model; Gaussian increments also violate the bounded-increment condition used for the explicit nonasymptotic overshoot bound. Report failures as informative boundary cases rather than hiding them.'),
]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}}); nbf.write(nb,NB/'04_robustness_stress_tests.ipynb')

# Notebook 5 external replay
cells=common_setup('05 — External UCI HAR Sequential-Sensing Replay','External replay using the UCI Human Activity Recognition Using Smartphones dataset. The primary analysis is binary and theorem-aligned in structure; the six-class section is exploratory. This is not physical safety validation.')
cells += [
nbf.v4.new_code_cell("""import io, zipfile, urllib.request, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from gated_benchmarks import mean_ci, wilson_interval

UCI_URL='https://archive.ics.uci.edu/static/public/240/human%2Bactivity%2Brecognition%2Busing%2Bsmartphones.zip'
"""),
nbf.v4.new_code_cell("""def make_mock_har(seed=0,n_train=1200,n_test=500,n_features=80,n_classes=6):
    # Smoke-only proxy: accelerometer classes overlap substantially; gyroscope adds separation.
    rng=np.random.default_rng(seed); half=n_features//2; names=[]
    for j in range(n_features):
        names.append((f'tBodyAcc-mean()-X{j}' if j<half else f'tBodyGyro-mean()-X{j}'))
    direction_acc=rng.normal(size=half); direction_acc/=np.linalg.norm(direction_acc)
    direction_gyro=rng.normal(size=n_features-half); direction_gyro/=np.linalg.norm(direction_gyro)
    coords=np.linspace(-1,1,n_classes)
    means=np.zeros((n_classes,n_features))
    for k,c in enumerate(coords):
        means[k,:half]=0.45*c*direction_acc
        means[k,half:]=1.8*c*direction_gyro
    # Make activities 2 and 3 especially close under weak sensing but distinguishable with gyro.
    means[1,:half]=-.80*direction_acc; means[2,:half]=.80*direction_acc
    means[1,half:]=-1.50*direction_gyro; means[2,half:]=1.50*direction_gyro
    def sample(n):
        y=rng.integers(1,n_classes+1,n); X=np.vstack([rng.normal(means[k-1],.85) for k in y]); return pd.DataFrame(X,columns=names),pd.Series(y)
    Xtr,ytr=sample(n_train); Xte,yte=sample(n_test); return Xtr,ytr,Xte,yte,names

def load_uci_har(use_real=True):
    if not use_real:
        return make_mock_har()
    cache=ROOT/'results'/'uci_har.zip'
    if not cache.exists():
        print('Downloading UCI HAR (~58 MB)...')
        urllib.request.urlretrieve(UCI_URL,cache)
    with zipfile.ZipFile(cache) as z:
        prefix='UCI HAR Dataset/'
        feat=pd.read_csv(z.open(prefix+'features.txt'),sep=r'\\s+',header=None,names=['id','name'])['name'].astype(str).tolist()
        # Make duplicates unique without altering modality substrings.
        feat=[f'{name}__{i}' for i,name in enumerate(feat)]
        Xtr=pd.read_csv(z.open(prefix+'train/X_train.txt'),sep=r'\\s+',header=None,names=feat)
        ytr=pd.read_csv(z.open(prefix+'train/y_train.txt'),header=None)[0]
        Xte=pd.read_csv(z.open(prefix+'test/X_test.txt'),sep=r'\\s+',header=None,names=feat)
        yte=pd.read_csv(z.open(prefix+'test/y_test.txt'),header=None)[0]
    return Xtr,ytr,Xte,yte,feat

USE_REAL = not SMOKE_TEST
try:
    Xtr,ytr,Xte,yte,feature_names=load_uci_har(USE_REAL)
    DATA_SOURCE='UCI HAR real data' if USE_REAL else 'mock smoke-test data'
except Exception as e:
    warnings.warn(f'Real download failed ({e}); using mock data for code validation only.')
    Xtr,ytr,Xte,yte,feature_names=make_mock_har(); DATA_SOURCE='mock fallback — NOT REPORTABLE'
print(DATA_SOURCE, Xtr.shape, Xte.shape, sorted(ytr.unique()))
"""),
nbf.v4.new_markdown_cell('## 1. Define weak vs strong sensor channels\nWeak channel uses accelerometer-derived features. Strong channel uses both accelerometer and gyroscope-derived features. The official UCI HAR dataset (Reyes-Ortiz et al., DOI: 10.24432/C54S4K) contains 10,299 windows from 30 volunteers performing six activities, using waist-mounted accelerometer and gyroscope sensing. The original subject-level train/test partition is retained.'),
nbf.v4.new_code_cell("""weak_cols=[c for c in Xtr.columns if 'Acc' in c and 'Gyro' not in c]
strong_cols=[c for c in Xtr.columns if ('Acc' in c or 'Gyro' in c)]
if len(weak_cols)<5: weak_cols=list(Xtr.columns[:max(5,Xtr.shape[1]//2)])
if len(strong_cols)<=len(weak_cols): strong_cols=list(Xtr.columns)
print('weak features',len(weak_cols),'strong features',len(strong_cols))
"""),
nbf.v4.new_code_cell("""def fit_density(X,y,cols,n_components):
    sc=StandardScaler().fit(X[cols]); Z=sc.transform(X[cols]); ncomp=min(n_components,Z.shape[1],max(2,Z.shape[0]-1)); pca=PCA(n_components=ncomp,random_state=0).fit(Z); Q=pca.transform(Z); g=GaussianNB(var_smoothing=1e-6).fit(Q,y); return sc,pca,g,cols

def class_loglik(model,Xrow):
    sc,pca,g,cols=model; q=pca.transform(sc.transform(pd.DataFrame([Xrow[cols].to_numpy()],columns=cols)))[0]
    var=g.var_; theta=g.theta_; return -0.5*np.sum(np.log(2*np.pi*var)+(q[None,:]-theta)**2/var,axis=1)

def batch_class_loglik(model,X):
    # Vectorized density table: rows x classes. Faster than transforming each replayed window repeatedly.
    sc,pca,g,cols=model
    Q=pca.transform(sc.transform(X[cols]))
    var=g.var_[None,:,:]; theta=g.theta_[None,:,:]
    QQ=Q[:,None,:]
    return -0.5*np.sum(np.log(2*np.pi*var)+(QQ-theta)**2/var,axis=2)
"""),
nbf.v4.new_markdown_cell('## 2. Binary external replay: WALKING_UPSTAIRS (2) vs WALKING_DOWNSTAIRS (3)\nThis deliberately harder pair uses the public train split only for calibration and the public test split only for replay. Because the action-conditioned densities are **estimated** rather than known, this is an external generalization check, not a proof of the theorem assumptions.'),
nbf.v4.new_code_cell("""classes=[2,3]; tr=ytr.isin(classes); te=yte.isin(classes)
Xbtr=Xtr.loc[tr].reset_index(drop=True); ybtr=ytr.loc[tr].reset_index(drop=True)
Xbte=Xte.loc[te].reset_index(drop=True); ybte=yte.loc[te].reset_index(drop=True)
wm=fit_density(Xbtr,ybtr,weak_cols,10); sm=fit_density(Xbtr,ybtr,strong_cols,20)
LLW_B=batch_class_loglik(wm,Xbte); LLS_B=batch_class_loglik(sm,Xbte)
print('test counts',ybte.value_counts().to_dict())
"""),
nbf.v4.new_code_cell("""def replay_binary(policy='gated',delta=.01,alpha=.05,n_trials=300,seed=0,max_steps=500):
    rng=np.random.default_rng(seed); A=math.log(1/delta); B=math.log(1/alpha); rows=[]
    cl=list(wm[2].classes_); i0=cl.index(2); i1=cl.index(3)
    pools={h:np.flatnonzero(ybte.to_numpy()==h) for h in classes}
    for h in classes:
        for tr in range(n_trials):
            S=M=0.; unlocked=(policy=='oracle'); nw=ns=0; dec=None
            for t in range(1,max_steps+1):
                idx=int(rng.choice(pools[h])); use_strong=(unlocked and policy!='weak_only') or policy=='oracle'
                ll=LLS_B[idx] if use_strong else LLW_B[idx]; inc=float(ll[i0]-ll[i1]); S+=inc; M=max(M,S)
                if use_strong: ns+=1
                else: nw+=1
                if policy=='gated' and (not unlocked) and M>=B: unlocked=True
                if S>=A: dec=2; break
                if S<=-A: dec=3; break
            if dec is None: dec=2 if S>=0 else 3
            rows.append({'true_class':h,'decision':dec,'error':int(dec!=h),'tau':nw+ns,'Nweak':nw,'Nstrong':ns,'unlocked':int(unlocked)})
    return pd.DataFrame(rows)

nrep=20 if SMOKE_TEST else (300 if not FULL_RUN else 2000)
rows=[]
for pol in ['gated','oracle','weak_only']:
    r=replay_binary(pol,n_trials=nrep,seed=10+['gated','oracle','weak_only'].index(pol))
    for h in classes:
        q=r[r.true_class==h]; rows.append({'policy':pol,'true_class':h,'mean_tau':q.tau.mean(),'error_rate':q.error.mean(),'mean_Nweak':q.Nweak.mean(),'mean_Nstrong':q.Nstrong.mean(),'unlock_rate':q.unlocked.mean()})
extbin=pd.DataFrame(rows); display(extbin); extbin.to_csv(ROOT/'results'/'uci_har_binary_replay.csv',index=False)
"""),
nbf.v4.new_markdown_cell('## 3. Six-class exploratory replay\nA second section keeps all six activities. It uses a confidence-gated switch from weak to strong sensor models. This is **not** the matched binary theorem; it is an external multi-hypothesis stress test.'),
nbf.v4.new_code_cell("""wm6=fit_density(Xtr,ytr,weak_cols,3); sm6=fit_density(Xtr,ytr,strong_cols,8)
LLW6=batch_class_loglik(wm6,Xte); LLS6=batch_class_loglik(sm6,Xte)
classes6=list(wm6[2].classes_); pools6={h:np.flatnonzero(yte.to_numpy()==h) for h in classes6}

def replay_multi(delta=.1,cert_margin=2.0,n_trials_per_class=25,seed=0,max_steps=200):
    rng=np.random.default_rng(seed); A=math.log((len(classes6)-1)/delta); rows=[]
    for h in classes6:
        for tr in range(n_trials_per_class):
            scores=np.zeros(len(classes6)); unlocked=False; nw=ns=0; dec=None
            for t in range(1,max_steps+1):
                idx=int(rng.choice(pools6[h])); ll=LLS6[idx] if unlocked else LLW6[idx]; scores+=ll
                if unlocked: ns+=1
                else: nw+=1
                order=np.argsort(scores)[::-1]; margin=scores[order[0]]-scores[order[1]]
                if not unlocked and margin>=cert_margin: unlocked=True
                if margin>=A: dec=classes6[order[0]]; break
            if dec is None: dec=classes6[int(np.argmax(scores))]
            rows.append({'true_class':h,'decision':dec,'error':int(dec!=h),'tau':nw+ns,'Nweak':nw,'Nstrong':ns,'unlocked':int(unlocked)})
    return pd.DataFrame(rows)
rm=replay_multi(n_trials_per_class=(3 if SMOKE_TEST else (25 if not FULL_RUN else 100)),seed=55)
summary6=rm.groupby('true_class').agg(mean_tau=('tau','mean'),error_rate=('error','mean'),strong_use=('Nstrong','mean')).reset_index(); display(summary6); summary6.to_csv(ROOT/'results'/'uci_har_sixclass_replay.csv',index=False)
"""),
nbf.v4.new_markdown_cell("## 4. PRISM follow-on protocol\nFor a robotics-specific replay, replace the UCI channel definitions with PRISM modalities: weak = robot state + low-risk force/torque summary; strong = tactile + richer force/torque/RGB-D features. Keep the wording **offline replay/counterfactual instantiation**, because a passive dataset cannot prove physical safety of an action gate. PRISM is large, so it is intentionally not downloaded automatically by this lightweight notebook."),
nbf.v4.new_markdown_cell("## Reporting guardrail\nFor the paper, call this section **External sequential-sensing replay**. Do not call it 'real-world safety validation.' The public data establish that the gating machinery can be instantiated with estimated action/sensor-conditioned models; they do not establish the physical safety semantics assumed by a real robot certificate."),
]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}}); nbf.write(nb,NB/'05_external_uci_har_replay.ipynb')

print('Wrote notebooks:', [p.name for p in sorted(NB.glob('*.ipynb'))])
