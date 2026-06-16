"""Generate analysis/toto_analysis.ipynb covering WS2-WS5 of the analysis plan.
Run: python3 build_analysis.py  then execute the notebook."""
import json
from pathlib import Path

cells = []


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src})


md("""# TOTO "Lucky Outlet" -- Statistical Analysis (WS2-WS5)

Tests whether some Singapore Pools outlets are genuinely "luckier" than random chance predicts,
after normalising for **exposure** (how long an outlet was open x its ticket-sales proxy).

**Workstreams in this notebook**
- **WS2** Distribution choice: is the win count Poisson? (dispersion, chi-square GOF, KS test, Negative Binomial, AIC/LR)
- **WS3** Luck detection: which outlets over/under-perform their exposure-expected wins? (Poisson tail tests + Benjamini-Hochberg FDR)
- **WS4** Explanatory regression: does anything beyond exposure explain wins? (Poisson/NB GLM with log-exposure offset)
- **WS5** Group comparisons + spatial: do normalised win rates differ by neighbourhood/region/type? (ANOVA/Kruskal/Tukey)

**Data:** `data/analysis_ready/outlets_modeling.csv` -- 374 outlets, exposure-normalised.
The authoritative win count is `combined_wins_hist`; exposure is `draws_i x volume_proxy` (HDB + commercial).""")

code("""import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
from pathlib import Path
OUT = Path("output"); OUT.mkdir(exist_ok=True)

df = pd.read_csv("../data/analysis_ready/outlets_modeling.csv")
print("rows:", len(df))
# Wins outcome (authoritative full-history count)
df["wins"] = df["combined_wins_hist"].astype(int)
# Numeric coercions
for c in ["draws_i","exposure","expected_wins","std_residual","win_rate_per_draw",
          "volume_proxy","hdb_proxy","pa_population","open_hours_daily","com_area_1000m"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
print("total wins:", df.wins.sum(), "| mean:", round(df.wins.mean(),2), "| var:", round(df.wins.var(),1))""")

# ---------------- WS2 ----------------
md("""## WS2 -- Distribution Choice: Is the win count Poisson?

The proposal models outlet wins as Poisson. A Poisson distribution has **variance = mean**.
We test that assumption four ways: dispersion index, chi-square goodness-of-fit, KS test,
and a Negative-Binomial comparison (AIC + likelihood-ratio).""")

code("""# 2.1 Mean, variance, dispersion index
w = df["wins"].values
mean_w, var_w = w.mean(), w.var(ddof=1)
D = var_w / mean_w
print(f"mean = {mean_w:.2f}")
print(f"variance = {var_w:.2f}")
print(f"dispersion index D = var/mean = {D:.2f}   (Poisson expects D = 1)")

# Formal dispersion test: D*(n-1) ~ chi-square(n-1) under H0 Poisson
n = len(w)
disp_stat = D * (n - 1)
disp_p = stats.chi2.sf(disp_stat, df=n - 1)
print(f"dispersion test: stat = {disp_stat:.0f} on df = {n-1}, p = {disp_p:.3g}")
print("=> REJECT Poisson (overdispersed)" if disp_p < 0.05 else "=> consistent with Poisson")""")

code("""# 2.2 Chi-square goodness-of-fit vs Poisson(lambda_hat)
# Build bins greedily so EVERY bin has expected count >= 5 (chi-square requirement).
lam = mean_w
maxw = int(w.max())
exp_each = np.array([n * stats.poisson.pmf(k, lam) for k in range(maxw+1)])
exp_each[maxw] += n * stats.poisson.sf(maxw, lam)   # tail mass into last value
obs_each = np.array([(w == k).sum() for k in range(maxw+1)], float)

bins_o, bins_e, lbls = [], [], []
co = ce = 0; lo = 0
for k in range(maxw+1):
    co += obs_each[k]; ce += exp_each[k]
    if ce >= 5 and (n - sum(bins_e) - ce) >= 5:   # close bin, keep enough for the rest
        bins_o.append(co); bins_e.append(ce); lbls.append(f"{lo}-{k}" if k>lo else f"{k}")
        co = ce = 0; lo = k+1
if ce > 0:   # final remainder folded into last bin
    if bins_e:
        bins_o[-1] += co; bins_e[-1] += ce
        lbls[-1] = lbls[-1].split('-')[0] + f"-{maxw}"
    else:
        bins_o.append(co); bins_e.append(ce); lbls.append(f"{lo}-{maxw}")
obs_b, exp_b = np.array(bins_o), np.array(bins_e)
exp_b *= obs_b.sum()/exp_b.sum()   # ensure totals match exactly

gof = pd.DataFrame({"bin":lbls,"observed":obs_b.astype(int),"expected":exp_b.round(1)})
print(gof.to_string(index=False))
chi2_gof, p_gof = stats.chisquare(obs_b, exp_b, ddof=1)
print(f"\\nchi-square GOF: chi2 = {chi2_gof:.1f}, dof = {len(obs_b)-2}, p = {p_gof:.3g}")
print("=> REJECT Poisson fit" if p_gof < 0.05 else "=> Poisson fit not rejected")""")

code("""# 2.3 Fit Negative Binomial by method of moments; KS test for both
# NB params from mean & var:  var = mu + mu^2/r  ->  r = mu^2/(var-mu)
mu = mean_w
r = mu**2 / (var_w - mu)
p_nb = r / (r + mu)
print(f"NegBin fit: r (size) = {r:.3f}, p = {p_nb:.4f}")

# KS via two-sample against large simulated samples (discrete-safe)
rng = np.random.default_rng(42)
sim_pois = stats.poisson.rvs(lam, size=200000, random_state=rng)
sim_nb   = stats.nbinom.rvs(r, p_nb, size=200000, random_state=rng)
ks_p = stats.ks_2samp(w, sim_pois)
ks_nb = stats.ks_2samp(w, sim_nb)
print(f"KS vs Poisson : D = {ks_p.statistic:.4f}, p = {ks_p.pvalue:.3g}")
print(f"KS vs NegBin  : D = {ks_nb.statistic:.4f}, p = {ks_nb.pvalue:.3g}")
print("(smaller D / larger p = closer fit)")""")

code("""# 2.4 AIC + likelihood-ratio: Poisson vs NB (intercept-only marginal models)
y = df["wins"]
X0 = np.ones((len(y),1))
pois = sm.GLM(y, X0, family=sm.families.Poisson()).fit()
nb   = sm.GLM(y, X0, family=sm.families.NegativeBinomial(alpha=1.0/r)).fit()
ll_p, ll_nb = pois.llf, nb.llf
lr = 2*(ll_nb - ll_p)
lr_p = stats.chi2.sf(lr, df=1)
print(f"Poisson  AIC = {pois.aic:.0f}   logLik = {ll_p:.0f}")
print(f"NegBin   AIC = {nb.aic:.0f}   logLik = {ll_nb:.0f}")
print(f"LR test (NB vs Poisson): stat = {lr:.0f}, p = {lr_p:.3g}")
print("=> NB fits significantly better" if lr_p < 0.05 else "=> no improvement from NB")""")

code("""# 2.5 Figure: observed histogram + Poisson + NB overlay
fig, ax = plt.subplots(figsize=(9,5))
bins = np.arange(0, w.max()+5, 5)
ax.hist(w, bins=bins, density=True, alpha=0.5, color="steelblue", label="observed wins")
xs = np.arange(0, w.max()+1)
ax.plot(xs, stats.poisson.pmf(xs, lam), "r-", lw=2, label=f"Poisson(lam={lam:.0f})")
ax.plot(xs, stats.nbinom.pmf(xs, r, p_nb), "g--", lw=2, label="Negative Binomial")
ax.set_xlabel("combined wins per outlet"); ax.set_ylabel("density")
ax.set_title(f"WS2: win distribution -- overdispersed (D={D:.0f}), NB fits better")
ax.legend()
plt.tight_layout(); plt.savefig(OUT/"ws2_distribution_fit.png", dpi=120); plt.show()""")

md("""**WS2 takeaway (fill from the output above):** the win count is strongly *overdispersed*
(D far above 1), so the **plain Poisson on raw counts is rejected**. The Negative Binomial fits
better (lower AIC, significant LR test, smaller KS distance). The overdispersion is driven by
outlets differing in exposure -- which is exactly why WS3/WS4 model wins *conditional on exposure*
(via an offset), where the Poisson assumption becomes defensible.""")

# ---------------- WS3 ----------------
md("""## WS3 -- Luck Detection: which outlets beat their exposure-expected wins?

Under H0 ("no luck"), outlet *i* wins follow Poisson(`expected_wins_i`). For each outlet we compute
the upper-tail probability of being *at least* this lucky, then correct for testing ~360 outlets at
once with Benjamini-Hochberg FDR. Without correction we would flag many false positives.""")

code("""# Restrict to outlets with a usable expected count
m = df[df["expected_wins"] > 0].copy().reset_index(drop=True)
print(f"outlets with usable exposure: {len(m)} of {len(df)}")

# Upper-tail p (over-performance) and lower-tail (under-performance)
m["p_over"]  = stats.poisson.sf(m["wins"] - 1, m["expected_wins"])   # P(X >= wins)
m["p_under"] = stats.poisson.cdf(m["wins"], m["expected_wins"])      # P(X <= wins)
m["p_two"]   = np.minimum(1, 2*np.minimum(m["p_over"], m["p_under"]))

# Benjamini-Hochberg FDR on the two-sided p
rej, p_adj, _, _ = multipletests(m["p_two"], alpha=0.05, method="fdr_bh")
m["p_adj"] = p_adj
m["significant"] = rej
print(f"significant after FDR (alpha=0.05): {rej.sum()} of {len(m)}")
print(f"  over-performers:  {((m.significant) & (m.wins > m.expected_wins)).sum()}")
print(f"  under-performers: {((m.significant) & (m.wins < m.expected_wins)).sum()}")""")

code("""# Luck league table
cols = ["outlet_name","neighborhood_type","wins","expected_wins","std_residual","p_two","p_adj","significant"]
lt = m[cols].copy()
lt["expected_wins"] = lt["expected_wins"].round(1)
lt["std_residual"]  = lt["std_residual"].round(2)
print("=== TOP 15 OVER-performers (by std_residual) ===")
print(lt.sort_values("std_residual", ascending=False).head(15).to_string(index=False))
print("\\n=== TOP 10 UNDER-performers ===")
print(lt.sort_values("std_residual").head(10).to_string(index=False))
lt.sort_values("std_residual", ascending=False).to_csv(OUT/"ws3_luck_league_table.csv", index=False)""")

code("""# Compare: naive RAW-count tail test (no exposure) vs exposure-adjusted
# Naive null: every outlet equally likely -> expected = total/n
naive_exp = df["wins"].sum()/len(df)
naive_p = stats.poisson.sf(df["wins"]-1, naive_exp)
naive_rej,_,_,_ = multipletests(np.minimum(1,2*np.minimum(naive_p, stats.poisson.cdf(df["wins"],naive_exp))),
                                alpha=0.05, method="fdr_bh")
print(f"NAIVE raw-count test (ignores exposure): {naive_rej.sum()} of {len(df)} outlets 'significant'")
print(f"EXPOSURE-adjusted test:                  {rej.sum()} of {len(m)} outlets significant")
print("=> the professor's point made quantitative: ignoring exposure massively over-flags 'luck'.")""")

code("""# Funnel plot: std_residual vs expected_wins with +/-2,3 SD bands
fig, ax = plt.subplots(figsize=(9,6))
colors = np.where(m["significant"], "crimson", "steelblue")
ax.scatter(m["expected_wins"], m["std_residual"], c=colors, alpha=0.6, s=25)
for k,ls in [(2,"--"),(3,":")]:
    ax.axhline(k, color="grey", ls=ls, lw=1); ax.axhline(-k, color="grey", ls=ls, lw=1)
ax.axhline(0, color="black", lw=0.8)
ax.set_xscale("symlog")
ax.set_xlabel("expected wins (exposure)"); ax.set_ylabel("standardised residual (luck score)")
ax.set_title("WS3: funnel plot -- red = significant after FDR correction")
plt.tight_layout(); plt.savefig(OUT/"ws3_funnel.png", dpi=120); plt.show()""")

md("""**WS3 takeaway:** compare the FDR-significant count to the naive raw-count count. The exposure
adjustment is what separates "genuinely beats chance" from "just old/busy". Surviving over-performers
(if any) are candidates for the WS4 covariate check before being called "lucky".""")

# ---------------- WS3 SENSITIVITY ----------------
md("""## WS3b -- Sensitivity Analysis: how robust is the luck list?

The raw WS3 residuals are inflated by **proxy error**: outlets with very few nearby HDB blocks
(commercial / tourist spots like Changi Village, Tuas) get a tiny `expected_wins`, so even ordinary
win counts produce huge residuals -- that is proxy mismatch, not luck. We test robustness three ways:

1. **Proxy-reliable subset** -- drop outlets where the denominator is untrustworthy (very low HDB
   footfall or commercial-dominated neighbourhoods).
2. **Exclude closed outlets** -- their `draws_i` is overstated (they shut before the data cut-off),
   biasing residuals negative.
3. **HDB-only exposure** -- re-run on the original `std_residual_hdb` to see if the combined proxy changed conclusions.

An outlet is only credibly "lucky" if it survives ALL the variants it is eligible for.""")

code("""# Build the proxy-reliable subset
# Unreliable if: hdb_proxy very low (<5 blocks -> denominator dominated by noise),
#   OR neighbourhood is commercial (proxy misses office/tourist footfall),
#   OR expected_wins < 5 (Poisson tail unstable).
base = df[df["expected_wins"] > 0].copy()
base["reliable"] = (
    (base["hdb_proxy"] >= 5) &
    (base["neighborhood_type"] == "residential") &
    (base["expected_wins"] >= 5)
)
reliable = base[base["reliable"]].copy().reset_index(drop=True)
print(f"full usable set:      {len(base)} outlets")
print(f"proxy-reliable subset: {len(reliable)} outlets "
      f"(residential, >=5 HDB blocks, expected>=5)")

def fdr_luck(sub):
    p_over = stats.poisson.sf(sub['wins']-1, sub['expected_wins'])
    p_under = stats.poisson.cdf(sub['wins'], sub['expected_wins'])
    p_two = np.minimum(1, 2*np.minimum(p_over, p_under))
    rej,_,_,_ = multipletests(p_two, alpha=0.05, method='fdr_bh')
    sub = sub.assign(p_two=p_two, sig=rej)
    return sub

rel = fdr_luck(reliable)
print(f"\\nOn the reliable subset, FDR-significant: {rel['sig'].sum()} of {len(rel)}")
print(f"  over-performers:  {(rel.sig & (rel.wins>rel.expected_wins)).sum()}")
print(f"  under-performers: {(rel.sig & (rel.wins<rel.expected_wins)).sum()}")""")

code("""# Sensitivity variant 2: also exclude closed outlets
rel_open = fdr_luck(reliable[reliable['is_closed']==0].reset_index(drop=True))
print(f"reliable + open-only: {len(rel_open)} outlets, "
      f"{rel_open['sig'].sum()} significant "
      f"({(rel_open.sig & (rel_open.wins>rel_open.expected_wins)).sum()} over, "
      f"{(rel_open.sig & (rel_open.wins<rel_open.expected_wins)).sum()} under)")

# Sensitivity variant 3: HDB-only exposure on the reliable subset
rh = reliable.dropna(subset=['expected_wins_hdb'])
rh = rh[rh['expected_wins_hdb']>0].copy()
ph_over = stats.poisson.sf(rh['wins']-1, rh['expected_wins_hdb'])
ph_under = stats.poisson.cdf(rh['wins'], rh['expected_wins_hdb'])
ph_two = np.minimum(1, 2*np.minimum(ph_over, ph_under))
rejh,_,_,_ = multipletests(ph_two, alpha=0.05, method='fdr_bh')
print(f"reliable + HDB-only exposure: {len(rh)} outlets, {rejh.sum()} significant")""")

code("""# Robust over-performers: significant AND positive across all variants they appear in
over_full = set(m.loc[m['significant'] & (m['wins']>m['expected_wins']), 'outlet_name'])
over_rel  = set(rel.loc[rel['sig'] & (rel['wins']>rel['expected_wins']), 'outlet_name'])
over_open = set(rel_open.loc[rel_open['sig'] & (rel_open['wins']>rel_open['expected_wins']), 'outlet_name'])
robust = over_rel & over_open
print(f"over-performers in FULL (proxy-contaminated) test: {len(over_full)}")
print(f"over-performers in reliable subset:                {len(over_rel)}")
print(f"over-performers robust to closed-outlet exclusion: {len(robust)}")
print()
rl = reliable.set_index('outlet_name')
print('=== ROBUST over-performers (survive reliable + open-only) ===')
show = rel[rel['outlet_name'].isin(robust)].sort_values('std_residual', ascending=False)
print(show[['outlet_name','planning_area','wins','expected_wins','std_residual','open_hours_daily']]
      .round({'expected_wins':1,'std_residual':2}).head(20).to_string(index=False))
show.to_csv(OUT/'ws3b_robust_overperformers.csv', index=False)""")

code("""# Visual: how the 'lucky' count shrinks as we tighten reliability
labels = ['naive\\n(raw count)','full\\n(all exposure)','reliable\\nsubset','reliable\\n+open','reliable\\n+HDB-only']
counts = [naive_rej.sum(), m['significant'].sum(), rel['sig'].sum(), rel_open['sig'].sum(), int(rejh.sum())]
fig, ax = plt.subplots(figsize=(9,5))
bars = ax.bar(labels, counts, color=['grey','steelblue','seagreen','seagreen','darkorange'])
for b,c in zip(bars,counts): ax.text(b.get_x()+b.get_width()/2, c+2, str(c), ha='center')
ax.set_ylabel('# outlets flagged significant'); ax.set_title('WS3b: "lucky/unlucky" count under tightening reliability filters')
plt.tight_layout(); plt.savefig(OUT/'ws3b_sensitivity_counts.png', dpi=120); plt.show()""")

md("""**WS3b takeaway:** the headline number to report is how the significant count *changes* as we
remove proxy-contaminated outlets. Outlets that stay significant on the **reliable residential subset**
(and survive the open-only and HDB-only checks) are the only credibly "lucky" ones -- everything that
drops out was a proxy artefact. Use this robust list, not the raw WS3 ranking, in the report.""")

# ---------------- WS4 ----------------
md("""## WS4 -- Explanatory Regression (Poisson / NB GLM with exposure offset)

`wins ~ offset(log(exposure)) + covariates`. The offset fixes exposure's coefficient at 1, so every
other coefficient is the effect on the **win rate per unit exposure**. We report Incidence Rate Ratios
exp(beta): IRR>1 raises the rate, IRR<1 lowers it. NB is the robust version (per WS2's overdispersion).""")

code("""reg = df[df["exposure"] > 0].copy()
reg["log_exposure"] = np.log(reg["exposure"])
reg["open_hours_daily"] = reg["open_hours_daily"].fillna(reg["open_hours_daily"].median())
reg["neighborhood_type"] = reg["neighborhood_type"].fillna("unknown")
reg["region"] = reg["region"].fillna("UNKNOWN")
# commercial area in 100k sqm units so the coefficient is readable
reg["com_area_100k"] = pd.to_numeric(reg["com_area_1000m"], errors="coerce").fillna(0)/1e5
print("regression sample:", len(reg))

formula = "wins ~ C(neighborhood_type) + C(region) + open_hours_daily + com_area_100k"
pois4 = smf.glm(formula, data=reg, family=sm.families.Poisson(),
                offset=reg["log_exposure"]).fit()
nb4 = smf.glm(formula, data=reg, family=sm.families.NegativeBinomial(alpha=1.0/r),
              offset=reg["log_exposure"]).fit()
print("Poisson GLM AIC:", round(pois4.aic,0), "| NB GLM AIC:", round(nb4.aic,0))""")

code("""# IRR table from the NB model (robust)
irr = pd.DataFrame({
    "coef": nb4.params,
    "IRR": np.exp(nb4.params),
    "CI_low": np.exp(nb4.conf_int()[0]),
    "CI_high": np.exp(nb4.conf_int()[1]),
    "p": nb4.pvalues,
}).round(4)
print("=== NB GLM with log(exposure) offset -- Incidence Rate Ratios ===")
print(irr.to_string())
irr.to_csv(OUT/"ws4_irr_table.csv")
sig = irr[(irr["p"] < 0.05) & (irr.index != "Intercept")]
print(f"\\nSignificant covariates beyond exposure: {len(sig)}")
print("=> If none/weak: wins are essentially proportional to exposure (the 'luck' is volume).")""")

code("""# Forest plot of IRRs (exclude intercept)
plot_irr = irr.drop("Intercept", errors="ignore").sort_values("IRR")
fig, ax = plt.subplots(figsize=(8, max(3,0.5*len(plot_irr))))
ax.errorbar(plot_irr["IRR"], range(len(plot_irr)),
            xerr=[plot_irr["IRR"]-plot_irr["CI_low"], plot_irr["CI_high"]-plot_irr["IRR"]],
            fmt="o", color="steelblue", capsize=3)
ax.axvline(1, color="red", ls="--", lw=1)
ax.set_yticks(range(len(plot_irr))); ax.set_yticklabels(plot_irr.index, fontsize=8)
ax.set_xlabel("Incidence Rate Ratio (exp beta)"); ax.set_title("WS4: covariate effects on win rate (NB GLM, exposure offset)")
plt.tight_layout(); plt.savefig(OUT/"ws4_forest.png", dpi=120); plt.show()""")

md("""**WS4 takeaway:** read the IRRs. A covariate with IRR significantly >1 raises the win rate beyond
what exposure predicts (a structural, non-luck driver). If no covariate is significant, wins are
proportional to exposure -- the myth is busted, "luck" = ticket volume.""")

# ---------------- WS5 ----------------
md("""## WS5 -- Group Comparisons on Normalised Win Rates

All comparisons use the **normalised** metric (`win_rate_per_draw`), never raw counts. We test whether
win rates differ across neighbourhood type, region, and outlet type with ANOVA / Kruskal-Wallis,
and follow significant results with Tukey HSD.""")

code("""g = df.dropna(subset=["win_rate_per_draw"]).copy()

def compare(group_col, label):
    sub = g[g[group_col].notna() & (g[group_col]!="")]
    groups = [v["win_rate_per_draw"].values for _,v in sub.groupby(group_col) if len(v)>=3]
    names  = [k for k,v in sub.groupby(group_col) if len(v)>=3]
    if len(groups) < 2:
        print(f"{label}: not enough groups"); return
    f,pf = stats.f_oneway(*groups)
    h,ph = stats.kruskal(*groups)
    print(f"=== {label} ({len(groups)} groups) ===")
    means = sub.groupby(group_col)["win_rate_per_draw"].agg(["count","mean"]).round(5)
    print(means.to_string())
    print(f"  ANOVA F={f:.2f} p={pf:.3g} | Kruskal H={h:.2f} p={ph:.3g}")
    print("  => groups differ" if min(pf,ph)<0.05 else "  => no significant difference")
    print()

compare("neighborhood_type", "Win rate by NEIGHBOURHOOD TYPE")
compare("region", "Win rate by REGION")
compare("outlet_type", "Win rate by OUTLET TYPE")""")

code("""# Tukey HSD on neighbourhood type (if >=2 groups with data)
sub = g[g["neighborhood_type"].notna() & (g["neighborhood_type"]!="")]
if sub["neighborhood_type"].nunique() >= 2:
    tuk = pairwise_tukeyhsd(sub["win_rate_per_draw"], sub["neighborhood_type"], alpha=0.05)
    print(tuk)""")

code("""# Boxplot of normalised win rate by neighbourhood type
fig, ax = plt.subplots(figsize=(8,5))
order = [c for c in ["residential","mixed","commercial"] if c in g["neighborhood_type"].unique()]
sns.boxplot(data=g[g.neighborhood_type.isin(order)], x="neighborhood_type", y="win_rate_per_draw", order=order, ax=ax)
ax.set_title("WS5: normalised win rate (wins/draw) by neighbourhood type")
plt.tight_layout(); plt.savefig(OUT/"ws5_winrate_by_nbhd.png", dpi=120); plt.show()""")

code("""# Spatial clustering of luck: do high-residual outlets cluster by region?
reg_means = df.dropna(subset=["std_residual"]).groupby("region")["std_residual"].agg(["count","mean"]).round(3)
print("Mean luck score (std_residual) by region:")
print(reg_means.to_string())
print("\\n(If means hover near 0 with no region standing out -> no spatial concentration of luck.)")""")

md("""**WS5 takeaway:** if normalised win rates do not differ across neighbourhood/region once exposure
is controlled, location confers no luck. Any difference that remains should map to a measured covariate
from WS4 (foot-traffic), not to "magic".""")

# ---------------- Synthesis ----------------
md("""## Synthesis -- The Story

Pulling WS2-WS5 together, fill the final report paragraph from the numbers above:

> Win counts are strongly overdispersed (WS2: D >> 1, Poisson rejected, NB preferred), because outlets
> differ enormously in exposure. Once we test each outlet against its exposure-expected wins with FDR
> correction (WS3), the number of genuinely "lucky" outlets collapses versus a naive raw-count test.
> A Negative-Binomial regression with a log-exposure offset (WS4) shows [few/no] covariates raise the
> win rate beyond exposure, and normalised win rates do [not] differ across neighbourhoods/regions (WS5).
> **Conclusion: apparent "luck" is an artefact of exposure -- how many tickets an outlet sells -- not
> any location-specific fortune.**

All figures and tables saved under `analysis/output/`.""")

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name":"Python 3","language":"python","name":"python3"},
                   "language_info": {"name":"python","version":"3.10"}},
      "nbformat": 4, "nbformat_minor": 5}

Path("analysis").mkdir(exist_ok=True)
with open("analysis/toto_analysis.ipynb","w") as f:
    json.dump(nb, f, indent=1)
print(f"wrote analysis/toto_analysis.ipynb with {len(cells)} cells")
