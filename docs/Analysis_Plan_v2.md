# IS630 Group 1 -- TOTO "Lucky Outlet" Analysis Plan (v2, post-proposal feedback)

**Purpose:** This document is the complete, step-by-step plan to finish the analysis after the professor's proposal feedback. It tells each team member exactly what to do, which tool/function to use, what output to produce, and how to interpret it. Work is split into 5 workstreams (WS1-WS5) for 5 people.

**The professor gave two instructions. Both are now the spine of this plan:**

1. **Normalise wins so older outlets are not automatically "lucky."** Model wins as a *proportion / rate* (counts / exposure), not raw counts. This is handled in WS1 (build the exposure denominator) and used everywhere downstream.
2. **Justify the Poisson choice with a model-fit test (e.g. KS test, plus chi-square GOF, dispersion test, and a Negative-Binomial comparison).** This is WS2.

---

## 0. Why the feedback matters (read this first, everyone)

Our raw data has a hidden trap. The per-outlet winning history spans different lengths of time:

- 375 outlets, 19,489 winning records (3,739 Group 1 + 15,750 Group 2).
- Draw numbers in the data run from ~1194 to ~4182 (~2,988 possible draws in the window).
- **Each outlet's active period ranges from 1 to 30 years (median ~21).**

So an outlet open since 2001 has had thousands of draws to accumulate wins, while one opened in 2016 has had only a few hundred. If we rank outlets by raw `combined_wins`, we are mostly ranking them by *age and size*, not by *luck*. That is exactly the professor's point.

**The fix, in one sentence:** define each outlet's *exposure* (how many draws it was open x how many tickets it likely sold), and measure luck as **wins relative to expected-given-exposure**, never as raw counts.

---

## 1. The statistical model we are committing to (shared vocabulary)

Let outlet *i* have:

- `W_i` = observed Group 1+2 wins (our outcome).
- `E_i` = **expected** wins under the "no luck" null = `N_total x p_i`, where `p_i` is outlet *i*'s share of total ticket exposure.
- `exposure_i` = `draws_i x volume_proxy_i`
  - `draws_i` = number of TOTO draws the outlet was operating (longevity term -- fixes the "older = luckier" bias).
  - `volume_proxy_i` = ticket-sales proxy = nearby HDB dwelling units / residential density (we cannot see real sales, so we proxy).
- `p_i = exposure_i / sum_j(exposure_j)`.

**Null hypothesis (H0):** `W_i ~ Poisson(E_i)`. Wins are proportional to exposure; no outlet is "lucky."

**Three ways we will express "normalised wins" (compute all three in WS1):**

| Metric | Formula | Meaning |
|---|---|---|
| **Win rate** | `W_i / draws_i` | wins per draw -- removes the longevity bias directly |
| **Exposure share vs win share** | `W_i / sum(W)` compared to `E_i / sum(E)` | does this outlet capture more of the wins than its exposure justifies? |
| **Standardised residual ("luck score")** | `(W_i - E_i) / sqrt(E_i)` | z-score of over/under-performance; the headline "luck" number |

The standardised residual is the single most important derived column. A value of +3 means "this outlet won 3 standard deviations more than exposure predicts" -- *that* is a defensible operational definition of "lucky."

---

## 2. Data changes to make NOW (WS1 owns this; everyone depends on it)

The current `data/analysis_ready/outlets_geodata.csv` (375 rows, 44 columns) already has wins, HDB proxy, land use, operating hours, and `years_winning`. We must add the exposure and normalised-win columns before any modelling.

### Step-by-step (WS1)

**2.1 Build the per-outlet draw count (`draws_i`).**
- Source: `data/raw/outlet_win_history.csv` (columns: `outlet_name, draw_date, draw_number, prize_amount, bet_type, prize_group`).
- We do NOT have a record of every draw an outlet sold tickets for -- only draws it *won*. So `draws_i` (the true denominator) must be *estimated*. Use the best available proxy for the active window:
  - `first_seen_i` = earliest draw_number where the outlet appears (or `earliest_win_year`).
  - `last_seen_i` = latest draw_number in the whole dataset (the data cut-off, same for all outlets, since an open outlet is "eligible" every draw up to the cut-off).
  - `draws_i = last_global_draw - first_seen_i + 1`.
- Tool: `pandas` groupby on `outlet_name`, `min`/`max` of `draw_number`. Save as `exposure_draws`.
- **Caveat to document:** this assumes an outlet, once seen, stayed open continuously until the cut-off. For closed outlets (the 85 that shut), cap `last_seen_i` at their last winning draw + a small buffer. Flag these rows; report results with and without them (sensitivity analysis).

**2.2 Build the sales-volume proxy.**
- Already present: `hdb_blocks_1000m` (count of HDB blocks within 1km) and `res_area_1000m` (residential land area). Use `hdb_blocks_1000m` as the primary `volume_proxy_i`; keep `res_area_1000m` as an alternative for robustness.

**2.3 Compute exposure, expected wins, and the three normalised metrics.**
```python
df['exposure'] = df['draws_i'] * df['hdb_blocks_1000m']
df['p_share']  = df['exposure'] / df['exposure'].sum()
N = df['combined_wins'].sum()
df['expected_wins'] = N * df['p_share']
df['win_rate_per_draw'] = df['combined_wins'] / df['draws_i']
df['win_share'] = df['combined_wins'] / N
df['std_residual'] = (df['combined_wins'] - df['expected_wins']) / np.sqrt(df['expected_wins'])
```
- Tool: `pandas` + `numpy`.
- **Output:** `data/analysis_ready/outlets_modeling.csv` -- the geodata file plus `draws_i, exposure, p_share, expected_wins, win_rate_per_draw, win_share, std_residual`. THIS is the file all of WS2-WS5 use.

**2.4 Guardrails (document in the report):**
- Outlets with `expected_wins < 5` make the standardised residual unstable -- flag them; the chi-square GOF also needs expected counts >= 5 per bin.
- Build the model two ways: (a) Group 1+2 combined, (b) Group 1 only (jackpot, rarer, purer signal). Group 2 dominates counts (15,750 vs 3,739), so combined is mostly Group 2.

**Expected WS1 deliverable:** the `outlets_modeling.csv` file + a 1-page data-prep note explaining `draws_i` estimation and its caveats. Without this, nothing else can start, so WS1 must finish first (target: 2-3 days).

---

## 3. The 5 workstreams

Each workstream below has: **Objective -> Steps (with exact tools) -> Expected output -> How to interpret.** Person names are suggestions; swap as you like. WS1 is the dependency for all; WS2-WS5 run in parallel once `outlets_modeling.csv` exists.

---

### WS1 -- Data preparation & exposure normalisation (foundational)
**Owner suggestion:** the person most comfortable with pandas (data engineer role).

**Objective:** Produce `outlets_modeling.csv` with exposure, expected wins, and the three normalised-win metrics (Section 2). Resolve the "older outlet = lucky" bias at the data level.

**Steps & tools:**
1. Parse `outlet_win_history.csv`, compute `draws_i` per outlet (pandas groupby min/max draw_number). [Section 2.1]
2. Merge onto `outlets_geodata.csv` by `outlet_name`. Handle the 3 geocode-failed + closed outlets explicitly.
3. Compute `exposure, p_share, expected_wins, win_rate_per_draw, win_share, std_residual`. [Section 2.3]
4. Produce a data-quality table: # outlets, # with expected_wins<5, # closed, missing-value summary.

**Expected output:**
- `data/analysis_ready/outlets_modeling.csv`.
- A markdown/notebook section: data dictionary for the new columns + the `draws_i` caveat + sensitivity flag column `is_closed`.
- Two histograms: distribution of `combined_wins` (raw) vs `win_rate_per_draw` (normalised), side by side, to *visually demonstrate* that normalisation changes the ranking.

**How to interpret:** If the top-10 by raw wins differs substantially from the top-10 by `win_rate_per_draw` or `std_residual`, that is direct evidence the professor's concern was warranted -- include this comparison table in the report as the motivation for normalising. (Expect Tong Aik Huat, NTUC FairPrice NEX etc. to drop once normalised.)

---

### WS2 -- Distribution choice & Poisson fit justification (the professor's Comment 2)
**Owner suggestion:** the person comfortable with scipy/statsmodels distributions.

**Objective:** Rigorously justify (or reject) the Poisson model for outlet win counts, using a goodness-of-fit battery: dispersion test, chi-square GOF, KS test, and a Negative-Binomial comparison.

**Steps & tools:**

**2.1 Visual + descriptive first.**
- Histogram of `combined_wins` (and separately Group 1 wins). Overlay the Poisson(lambda-hat) PMF where `lambda_hat = mean(combined_wins)`.
- Tool: `matplotlib` + `scipy.stats.poisson.pmf`.
- Compute mean and variance of `combined_wins`.

**2.2 Dispersion test (the make-or-break check).**
- Compute the **index of dispersion** `D = variance / mean`. For a true Poisson, `D ~ 1`.
- Formal test: `D x (n-1) ~ chi-square(n-1)`. Tool: `scipy.stats.chi2.sf`.
- **Interpretation:** TOTO wins are very likely **overdispersed** (`D >> 1`) because outlets differ wildly in exposure. If overdispersed, plain Poisson on raw counts is *inadequate* -- this is itself a finding and motivates either (a) the exposure-offset Poisson GLM (WS4) or (b) a Negative Binomial. Say this explicitly; it shows you understood *why* the professor asked.

**2.3 Chi-square goodness-of-fit (standard discrete GOF).**
- Bin the observed win counts (e.g. 0, 1, 2, 3, 4, 5-9, 10+). Compute Poisson-expected frequencies for each bin from `lambda_hat`. Merge bins so every expected count >= 5.
- Test: `scipy.stats.chisquare(observed_freq, expected_freq)` with `ddof=1` (one parameter estimated).
- **Interpretation:** small p-value (< 0.05) => reject "wins are Poisson" => the simple Poisson does not fit; exposure heterogeneity matters.

**2.4 KS test (what the professor explicitly named).**
- The KS test compares two distributions. For our discrete counts use the **two-sample KS**: draw a large simulated sample from `Poisson(lambda_hat)` (e.g. 100,000 draws) and compare against the observed win counts.
- Tool: `scipy.stats.kstest(observed_counts, lambda x: scipy.stats.poisson.cdf(x, lambda_hat))` for one-sample, OR `scipy.stats.ks_2samp(observed_counts, simulated_poisson_sample)` for two-sample (more defensible on discrete data).
- Also run KS for the **Negative Binomial** fit (next step) and compare KS statistics -- the smaller KS statistic / larger p-value is the better-fitting distribution.
- **Interpretation:** report the KS statistic `D` and p-value for Poisson vs Negative Binomial. State which distribution the data is "closer to."

**2.5 Fit and compare Negative Binomial (the honest alternative).**
- Fit NB by method of moments or MLE. Tool: `scipy.stats.nbinom` (estimate `n, p` from mean and variance) or `statsmodels` `NegativeBinomial`.
- Compare Poisson vs NB by **AIC/BIC** (lower is better) and a **likelihood-ratio test** (NB nests Poisson as dispersion -> 0). Tool: `statsmodels` GLM with `family=Poisson` vs `NegativeBinomial`.
- **Interpretation:** if NB wins on AIC and the LR test is significant, conclude "counts are overdispersed; Negative Binomial is the appropriate marginal model, and the overdispersion is driven by exposure differences, which we model directly via the offset in WS4." This is a *strong, examiner-pleasing* narrative.

**Expected output (WS2):**
- One figure: observed histogram + Poisson PMF overlay + NB PMF overlay.
- One results table: mean, variance, dispersion index D and its p-value; chi-square GOF stat + p; KS stat + p (Poisson) and KS stat + p (NB); AIC/BIC for Poisson and NB; LR-test p.
- A 2-paragraph written justification of the final distribution choice.

**How to interpret the whole WS2:** The deliverable answers the professor's question "why Poisson?" honestly. Most likely conclusion: *raw* counts are overdispersed (Poisson rejected), which is precisely why we move to an **exposure-adjusted Poisson regression with an offset** (WS4) -- where, conditional on exposure, the Poisson assumption becomes defensible -- and we report NB as a robustness check. Document the KS and chi-square numbers as evidence.

---

### WS3 -- "Luck" detection: expected vs observed & multiple testing
**Owner suggestion:** the person comfortable with hypothesis testing.

**Objective:** Identify which outlets (if any) significantly over/under-perform their exposure-expected wins, correctly accounting for testing 375 outlets at once.

**Steps & tools:**
1. For each outlet compute the Poisson tail probability of being at least this lucky: `p_i = P(X >= W_i | Poisson(E_i)) = scipy.stats.poisson.sf(W_i - 1, E_i)`. (Use `E_i` from WS1, the exposure-expected count.)
2. Rank outlets by `std_residual` (from WS1) and by `p_i`.
3. **Multiple-testing correction (critical -- 375 simultaneous tests):** apply Benjamini-Hochberg FDR or Bonferroni. Tool: `statsmodels.stats.multitest.multipletests(pvals, method='fdr_bh')`.
4. Produce the "luck league table": outlet, W_i, E_i, std_residual, raw p, adjusted p, significant flag.

**Expected output:**
- The luck league table (top 15 over-performers, top 15 under-performers).
- A funnel plot: `std_residual` (y) vs `expected_wins` (x) with +/-2 and +/-3 SD control limits -- the classic way to show which points breach random-variation bounds.
- Count of outlets still significant after FDR correction.

**How to interpret:**
- If **no** outlet survives FDR correction => strong evidence the "lucky outlet" belief is a myth: apparent luck is explained by exposure + random variation. (This is the most likely and most satisfying result.)
- If a **few** survive => name them, but check whether they are explained by WS4 covariates (e.g. they sit in extremely high-footfall spots) before calling them "lucky."
- Emphasise the difference between *raw* tail tests (which would flag many big old outlets) and *exposure-adjusted* tests -- this is the professor's point made quantitative.

---

### WS4 -- Explanatory modelling: Poisson/NB regression with exposure offset
**Owner suggestion:** the person comfortable with regression / statsmodels.

**Objective:** Explain win counts using exposure + spatial + operational covariates, with exposure entered correctly as an **offset** so the model estimates *rate per unit exposure* (directly answering "are wins just proportional to sales?").

**Steps & tools:**
1. Model: `combined_wins ~ offset(log(exposure)) + neighborhood_type + outlet_type + open_hours_daily + com_area_1000m + rc_ratio_1000m + region`.
   - Tool: `statsmodels.formula.api.glm` with `family=sm.families.Poisson()` and `offset=np.log(df['exposure'])`. Re-fit with `family=sm.families.NegativeBinomial()` for robustness (per WS2).
2. The offset forces the coefficient on exposure to 1 -- so every other coefficient is interpreted as effect on the *win rate*, holding exposure fixed.
3. Check residuals, pseudo-R^2, and coefficient significance. Report Incidence Rate Ratios `exp(beta)`.
4. Optionally a simpler OLS on `win_rate_per_draw` or `log(win_rate)` as an accessible cross-check (Sessions 7 linear regression).

**Expected output:**
- Regression table: coefficient, IRR `exp(beta)`, 95% CI, p-value for each predictor (Poisson and NB side by side).
- A coefficient/forest plot of the IRRs.
- Model-fit statistics (deviance, AIC, pseudo-R^2).

**How to interpret:**
- Significant covariate with IRR > 1 means that feature raises the win *rate* beyond what exposure alone predicts -- e.g. if `open_hours_daily` IRR = 1.05, each extra open-hour multiplies the rate by 1.05.
- If, after the offset, **no spatial/operational covariate is significant**, conclude wins are essentially proportional to exposure (sales) -- the myth is busted; "luck" = "more tickets sold."
- If commercial-cluster or operating-hours variables ARE significant, you have a structural (non-luck) explanation for the apparent luck -- also a great finding. Either way, "luck" is not random magic.

---

### WS5 -- Spatial analysis, group comparisons & synthesis
**Owner suggestion:** the person comfortable with geopandas/visualisation + the writer.

**Objective:** Test whether "luck" clusters geographically, compare normalised win rates across groups, and assemble the final narrative + visuals.

**Steps & tools:**
1. **Group comparisons on the NORMALISED metric** (not raw counts!): compare `win_rate_per_draw` (or `std_residual`) across `neighborhood_type` (residential/commercial/mixed), `region`, and `outlet_type`.
   - 3+ groups: one-way ANOVA `scipy.stats.f_oneway` if approx normal, else Kruskal-Wallis `scipy.stats.kruskal`; follow significant ANOVA with Tukey HSD `statsmodels.stats.multicomp.pairwise_tukeyhsd`.
   - 2 groups: two-sample t-test or Mann-Whitney.
2. **Spatial autocorrelation (optional, advanced):** Moran's I on `std_residual` to test whether high-luck outlets cluster. Tool: `libpysal` + `esda` (or report qualitatively from the map if libraries unavailable).
3. **Maps:** choropleth of mean `std_residual` by planning area; bubble map of outlets sized by `std_residual`, coloured by significance. Tool: `geopandas` + the planning-area GeoJSON.
4. **Synthesis:** assemble WS1-WS4 outputs into the report and slides; write the EDA section (distribution of normalised wins, correlation of `win_rate_per_draw` with HDB proxy).

**Expected output:**
- ANOVA/Kruskal tables + Tukey results on normalised metrics.
- 2 maps (choropleth + bubble).
- Final report sections + slide deck skeleton.

**How to interpret:**
- If normalised win rates do NOT differ across neighborhood types/regions => location does not confer luck once exposure is controlled (myth busted, cleanly).
- If they DO differ => identify whether it tracks a measured covariate from WS4 (foot-traffic, not magic).
- Moran's I near 0 => no spatial clustering of luck => consistent with randomness.

---

## 4. How the pieces answer the professor directly

| Professor's comment | Where addressed | The concrete deliverable |
|---|---|---|
| "Model counts as a proportion (counts / total draws) so older outlets are not automatically lucky" | WS1 (build exposure, win_rate_per_draw, expected_wins, std_residual); used in WS3/WS4/WS5 | `outlets_modeling.csv` + raw-vs-normalised top-10 comparison table + offset in the GLM |
| "Provide more detail on why Poisson was chosen; use model fit (KS test can test similarity between distributions)" | WS2 (dispersion test, chi-square GOF, KS test for Poisson & NB, AIC/BIC, LR test) | Fit-statistics table + PMF-overlay figure + written distribution-choice justification |

---

## 5. Suggested timeline (2-3 weeks to final)

| Phase | Days | Who | Gate |
|---|---|---|---|
| WS1 data prep | 1-3 | P1 | `outlets_modeling.csv` released to team |
| WS2, WS3, WS4, WS5 in parallel | 4-12 | P2, P3, P4, P5 | each produces its output table/figures |
| Integration & cross-checks | 13-16 | all | numbers reconciled across workstreams |
| Report + slides | 17-21 | P5 leads, all contribute | final artefacts |

**Cross-checks to run before submitting:** (a) does WS3's significant-outlet list shrink dramatically vs a naive raw-count test? (it should); (b) does WS2's overdispersion finding match WS4's need for NB / offset? (it should); (c) are all group comparisons in WS5 done on normalised metrics, never raw counts? (must be).

---

## 6. Tooling summary (install once)

```bash
pip install pandas numpy scipy statsmodels matplotlib seaborn geopandas libpysal esda
```

| Task | Library / function |
|---|---|
| Data wrangling | `pandas`, `numpy` |
| Poisson/NB PMF, tail probs | `scipy.stats.poisson`, `scipy.stats.nbinom` |
| Dispersion / chi-square GOF | `scipy.stats.chi2`, `scipy.stats.chisquare` |
| KS test | `scipy.stats.kstest`, `scipy.stats.ks_2samp` |
| GLM with offset, NB, AIC | `statsmodels.api.GLM`, `statsmodels.formula.api.glm` |
| Multiple-testing correction | `statsmodels.stats.multitest.multipletests` |
| ANOVA / Tukey / Kruskal | `scipy.stats.f_oneway`, `scipy.stats.kruskal`, `statsmodels.stats.multicomp.pairwise_tukeyhsd` |
| Maps / spatial autocorrelation | `geopandas`, `libpysal`, `esda.Moran` |

---

## 7. The one-paragraph story we are building toward

> "Belief in 'lucky' TOTO outlets is largely an artefact of exposure. Outlets that have been open longer and sit in denser areas naturally accumulate more winning tickets. Once we normalise wins by exposure (draws x sales proxy) and model counts with an exposure-offset Poisson/Negative-Binomial regression -- justified over a plain Poisson by dispersion, chi-square, and KS goodness-of-fit tests -- almost no outlet's win rate exceeds what random chance predicts. Apparent 'luck' is explained by how many tickets an outlet sells, not by any location-specific fortune."

That is the thesis. Every workstream produces one brick of evidence for it.
