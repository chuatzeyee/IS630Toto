# Improved Analytical Methodology

## Critical Assessment of the Current Proposal

### The Core Problem: IS630 Alignment

The current proposal designs six analysis threads, but most use techniques that are either partially covered or could be better aligned with the IS630 syllabus (Sessions 1-9). Three threads use techniques that have stronger IS630-native alternatives:

| Current Thread | IS630 Coverage | Risk |
|---|---|---|
| 1. Poisson GOF (equal-lambda) | Partially covered | Straw-man null hypothesis |
| 2. Volume-adjusted chi-squared + Monte Carlo | Partially covered | Monte Carlo not taught |
| 3. Bayesian Beta-Binomial | **Covered in Session 9** | Viable, but needs reformulation |
| 4. Moran's I spatial autocorrelation | **Not covered** | Specialized spatial statistics |
| 5. Wald-Wolfowitz runs test | **Not covered** | Not in the non-parametric toolkit taught |
| 6. Mann-Whitney U / Kruskal-Wallis | **Fully covered** | Best-aligned thread |

Meanwhile, the following **core IS630 techniques are completely absent** from the proposal:

- One-Way ANOVA, Tukey HSD (Session 6)
- Two-Way ANOVA with interaction terms (Session 6)
- Chi-Square Test of Independence (Session 6)
- Welch's t-test (Session 5)
- Confidence intervals -- single and two-population (Session 4)
- Shapiro-Wilk / Levene's assumption checking (Sessions 5-6)
- Kruskal-Wallis with Dunn's post-hoc (Session 6)
- **Simple and Multiple Linear Regression (Session 7)**
- **PCA / Dimensionality Reduction (Session 8)**
- Distribution fitting with scipy.stats (Session 3)
- Descriptive statistics and EDA (Sessions 1-2)

The rubric criterion "Understanding and application of statistical concepts in the context of the project" almost certainly means IS630 concepts. The current methodology neglects several major techniques being graded -- most critically, **linear regression** (Session 7) is the single most natural tool for modeling the relationship between volume and wins, and it is entirely absent.

### The Volume Proxy Problem

Every quantitative thread except Thread 1 depends on the HDB dwelling unit proxy for ticket sales volume. This proxy has a **systematic bias** that is not merely a limitation to footnote -- it potentially invalidates the central finding.

Commercial/tourist planning areas (Rochor, Outram, Downtown Core, Orchard) collectively account for approximately **28% of all physical-outlet Group 1 wins** but have among the lowest HDB dwelling unit counts. The proxy will systematically under-predict expected wins for these outlets, making them appear "lucky" in any volume-adjusted test. These are precisely the outlets (Delisia Agency at Fu Lu Shou Complex, People's Park Centre, Suntec City) that the public considers lucky.

The proxy must be validated and its failure modes explicitly handled **before** using it in any hypothesis test.

### The Straw-Man Null (Thread 1)

Thread 1 tests whether all outlets share the same Poisson rate lambda. This is trivially false because outlets sell vastly different volumes of tickets. Rejecting this null proves only that outlets differ in volume -- something everyone already knows. It contributes nothing to the "luck" question.

### Data Sparsity (Thread 5)

With ~550-650 Group 1 wins spread across 375 physical outlets, the median outlet has 1-2 Group 1 wins over 11 years. A runs test on a binary sequence with 2 ones among 1,200 trials is meaningless -- the test has zero power. The hot-hand thread cannot work at the per-outlet level with Group 1 data.

---

## Restructured Methodology

The improved methodology is organized as **seven phases** that form a coherent analytical narrative. Each phase maps directly to IS630 sessions, builds on the previous phase, and uses techniques the team has been taught.

### Overview

```
Phase 1: EDA & Descriptive Statistics          (Sessions 1-2)
    |
    v
Phase 2: Proxy Construction & Validation       (Sessions 1-2, 3)
    |
    v
Phase 3: Distribution Analysis                 (Session 3)
    |
    v
Phase 4: Hypothesis Testing                    (Sessions 4, 5, 6)
    |
    v
Phase 5: Regression Modeling                   (Session 7)
    |
    v
Phase 6: Bayesian Analysis                     (Session 9)
    |
    v
Phase 7: Synthesis & Robustness Checks         (Sessions 4-9)
```

---

### Phase 1: Exploratory Data Analysis and Descriptive Statistics

**IS630 Sessions:** 1 (Foundations), 2 (Descriptive Statistics & EDA)

**Goal:** Characterize the data before testing anything. Establish the patterns that the public perceives as "luck" and quantify the variation that needs explaining.

#### 1.1 Win Distribution Across Outlets

Compute and visualize the distribution of wins per outlet (separately for Group 1 only, Group 2 only, and combined):

- **Measures of center:** Mean, median, mode of wins per outlet
- **Measures of spread:** Standard deviation (`np.std(data, ddof=1)`), variance, IQR, range (`np.ptp`)
- **Shape:** Skewness (apply Bulmer's rule: <0.5 symmetric, 0.5-1.0 moderate, >=1.0 highly skewed)
- **Full summary:** `pd.Series(wins).describe()`
- **Visualization:** Histogram with kernel density overlay; boxplot showing outlier outlets (1.5x IQR rule)

**Key insight to establish:** The distribution of wins is highly right-skewed. A few outlets have many wins (Tong Aik Huat, Delisia Agency), while most outlets have 0-3 wins. This skew is what creates the "lucky outlet" perception.

```python
# IS630 Session 2 techniques
import numpy as np
import pandas as pd

wins = outlet_summary['group1_wins']
print(f"Mean: {np.mean(wins):.2f}")
print(f"Median: {np.median(wins):.2f}")
print(f"Std Dev: {np.std(wins, ddof=1):.2f}")      # sample std dev
print(f"IQR: {np.percentile(wins, 75) - np.percentile(wins, 25):.1f}")
print(f"Skewness: {pd.Series(wins).skew():.2f}")    # expect >= 1.0
```

#### 1.2 Scatter Plot: Volume Proxy vs Wins

Before any formal test, visualize the relationship that will drive the entire analysis:

- Scatter plot: x-axis = HDB dwelling units within 1km (proxy volume), y-axis = total wins
- Compute **Spearman rank correlation** (non-parametric, no normality assumption required)
- Annotate outlier outlets (those far from the trend line)

This single visualization immediately tells the reader whether volume explains wins. If the scatter shows a clear positive trend, the "volume explains luck" narrative is visually established before any test is run.

#### 1.3 Geographic Distribution

- Choropleth map of wins per planning area (using `geopandas` + URA planning area boundaries)
- Choropleth map of population density per planning area
- Side-by-side comparison: do the two maps look similar?
- Bar chart: top 10 planning areas by total wins vs top 10 by population

#### 1.4 Outlet Type Analysis

- Descriptive statistics by outlet type (Branch, Authorised Retailer, Betting Centre, Livewire)
- How do win counts differ across outlet types? (Table of means, medians, IQRs)
- Flag the Account Betting Service exclusion and quantify its impact (~28-30% of all Group 1 wins)

**Deliverable:** A clear descriptive picture showing that win variation exists, that it correlates visually with volume/population, and that commercial-area outlets are a distinct subgroup.

---

### Phase 2: Proxy Construction and Validation

**IS630 Sessions:** 1-2 (Data quality, EDA), 3 (Distributions)

**Goal:** Build the HDB dwelling unit volume proxy and explicitly assess its quality before using it in any hypothesis test. This is the most critical methodological step -- if the proxy is unreliable, every downstream test is compromised.

#### 2.1 Proxy Construction

For each physical outlet, compute:
```
proxy_volume_i = sum of HDB dwelling units within radius r of outlet i
```

Test with r = 500m, 750m, 1000m, 1500m. Store all four values.

#### 2.2 Sensitivity Analysis Across Radii

- Compute the Spearman rank correlation between proxy values at different radii
- How stable is the outlet ranking across r = 500m vs 1000m vs 1500m?
- If ranking changes dramatically with r, the proxy is unreliable

```python
# Rank stability across radii
from scipy.stats import spearmanr
rho, p = spearmanr(proxy_500m, proxy_1000m)
print(f"Spearman rank correlation (500m vs 1000m): rho={rho:.3f}, p={p:.5f}")
```

#### 2.3 Commercial vs Residential Classification

Classify each outlet as "residential" or "commercial" based on its planning area:
- **Commercial:** Rochor, Outram, Downtown Core, Orchard, Museum, Singapore River, Marina South
- **Residential:** All HDB-dominated planning areas (Bedok, Tampines, Yishun, Jurong West, etc.)

Report:
- Number of outlets in each category
- Mean Group 1 wins in each category
- Proportion of total wins from each category
- Mean proxy volume in each category

**Expected finding:** Commercial outlets have disproportionately more wins relative to their HDB proxy, confirming that the proxy under-estimates their true volume.

#### 2.4 Proxy Validation Summary

Explicitly state: "The HDB dwelling unit proxy is a reasonable estimate of foot traffic for **residential-area outlets** (~250 outlets, ~72% of physical outlets) but systematically underestimates volume for **commercial-area outlets** (~50 outlets, ~28% of wins). All volume-adjusted hypothesis tests in Phases 4-6 are reported separately for these two subgroups."

This honest framing strengthens the analysis. It is more rigorous to show that your proxy works for a well-defined subset than to pretend it works everywhere.

---

### Phase 3: Distribution Analysis

**IS630 Session:** 3 (Probability and Distributions)

**Goal:** Test whether win counts follow the theoretical distribution expected under pure randomness.

#### 3.1 Poisson Distribution Fit (Group 1 Wins Only)

If every ticket has the same probability of winning, and the number of tickets per outlet is roughly constant, then wins per outlet should follow a Poisson distribution. Since outlets do NOT sell the same volume, we test this in two ways.

**Test A: Raw Poisson Fit (Baseline)**

- Compute lambda = mean(group1_wins) across residential outlets only (~1.5-1.7)
- Bin outlets: 0 wins, 1 win, 2 wins, 3 wins, 4 wins, 5+ wins
- Compute expected frequencies from `stats.poisson.pmf(k, mu=lambda)` for each bin
- Chi-squared GOF: `scipy.stats.chisquare(observed_freq, f_exp=expected_freq)`

**Hypothesis:**
- H0: Group 1 wins across residential outlets follow Poisson(lambda)
- H1: The distribution does not follow Poisson(lambda)

**Expected result:** Reject H0. The variance-to-mean ratio (dispersion index) will exceed 1.0, indicating overdispersion. This establishes the puzzle: wins are not uniformly distributed, so is it luck or volume?

**IS630 Python:**
```python
from scipy import stats
import numpy as np

wins = residential_outlets['group1_wins'].values
lam = np.mean(wins)
n = len(wins)

# Compute expected frequencies
bins = [0, 1, 2, 3, 4]  # 5+ is the last bin
observed = [np.sum(wins == k) for k in bins] + [np.sum(wins >= 5)]
expected = [n * stats.poisson.pmf(k, mu=lam) for k in bins] + [n * stats.poisson.sf(4, mu=lam)]

chi2, p = stats.chisquare(observed, f_exp=expected)
dispersion = np.var(wins, ddof=1) / np.mean(wins)
print(f"Dispersion index: {dispersion:.2f} (Poisson requires ~1.0)")
print(f"Chi-squared: {chi2:.3f}, p-value: {p:.5f}")
```

**Visualization:** Overlay histogram (observed) with Poisson PMF (expected). The mismatch between the two is the visual hook for the entire project.

**Test B: Volume-Stratified Poisson Check**

To isolate volume from luck, divide outlets into 3 volume groups (terciles based on proxy) and test Poisson fit within each group:

- Compute lambda_group = mean(group1_wins) within each volume tercile
- Run the same chi-squared GOF within each group
- If the within-group distributions fit Poisson, then the overall overdispersion is explained by volume differences, not luck

This is the key insight: between-group overdispersion (caused by volume) vs within-group overdispersion (which would suggest luck). If within-group fit is Poisson, volume is sufficient.

---

### Phase 4: Hypothesis Testing

**IS630 Sessions:** 4 (Confidence Intervals), 5 (Hypothesis Testing I), 6 (Hypothesis Testing II)

This is the core of the project. Five tests, logically sequenced, each mapping to specific IS630 content.

#### 4.1 Chi-Squared Test of Independence: Region x Win Category

**IS630 Session 6:** Chi-Square Test of Independence

**Question:** Is there an association between geographic region and winning frequency? (Tests the "lucky neighborhood" myth)

**Setup:**
- Rows: 5 geographic regions (North, South, East, West, Central) or planning area groups
- Columns: Win category (0 wins, 1-2 wins, 3-5 wins, 6+ wins) -- adjust bin edges so no expected count is below 5
- Contingency table of observed frequencies

**Hypotheses:**
- H0: Win category is independent of geographic region
- H1: An association exists between region and win frequency

**Python (Session 6 technique):**
```python
from scipy.stats import chi2_contingency

# observed = contingency table (np.array)
chi2, p, dof, expected = chi2_contingency(observed, correction=False)
print(f"Chi-Square: {chi2:.3f}, df={dof}, p-value: {p:.5f}")

# Standardized residuals to identify which cells drive the result
std_resid = (observed - expected) / np.sqrt(expected)
print("Standardized Residuals (|value| > 2 = significant):")
print(std_resid)
```

**Interpretation:** If H0 is rejected, examine standardized residuals to identify which region-win combinations deviate from expectation. Then overlay with population density: do "lucky regions" simply have more people?

**Follow-up:** Repeat with a second contingency table using volume-adjusted categories instead of raw win counts. If the association disappears after adjustment, volume (population) explains the regional pattern entirely.

---

#### 4.2 One-Way ANOVA / Kruskal-Wallis: Win Rates Across Volume Groups

**IS630 Session 6:** One-Way ANOVA, Kruskal-Wallis, Tukey HSD, Dunn's test

**Question:** Do win rates differ across outlet volume groups? This is the central test -- after controlling for volume by grouping, do any volume groups win at a different rate?

**Setup:**
- Divide residential outlets into 3 groups by proxy volume tercile (Low / Medium / High)
- Response variable: win rate = group1_wins / proxy_volume_1000m (wins per 1000 HDB units)
- This normalizes by volume within each group

**Step 1: Check assumptions**
```python
from scipy import stats

# Normality of residuals (Shapiro-Wilk)
for group_name, group_data in groups:
    stat, p = stats.shapiro(group_data['win_rate'])
    print(f"{group_name}: Shapiro-Wilk p={p:.3f} -> {'Normal' if p > 0.05 else 'Non-normal'}")

# Equal variances (Levene's test)
stat, p = stats.levene(low['win_rate'], med['win_rate'], high['win_rate'])
print(f"Levene's test: p={p:.3f} -> {'Equal variance' if p > 0.05 else 'Unequal variance'}")
```

**Step 2: Choose test based on assumptions**

*If normality and equal variance hold:*
```python
# One-Way ANOVA (Session 6)
from scipy.stats import f_oneway
f_stat, p_val = f_oneway(low['win_rate'], med['win_rate'], high['win_rate'])
print(f"ANOVA: F={f_stat:.3f}, p={p_val:.5f}")

# If significant -> Tukey HSD post-hoc
from statsmodels.stats.multicomp import pairwise_tukeyhsd
tukey = pairwise_tukeyhsd(
    endog=df_residential['win_rate'],
    groups=df_residential['volume_group'],
    alpha=0.05
)
print(tukey.summary())
tukey.plot_simultaneous()
```

*If normality fails (likely given the skewed win distribution):*
```python
# Kruskal-Wallis (Session 6 non-parametric alternative)
h_stat, p_val = stats.kruskal(low['win_rate'], med['win_rate'], high['win_rate'])
print(f"Kruskal-Wallis: H={h_stat:.3f}, p={p_val:.5f}")

# If significant -> Dunn's post-hoc
import scikit_posthocs as sp
posthoc = sp.posthoc_dunn(
    df_residential, val_col='win_rate',
    group_col='volume_group', p_adjust='holm'
)
print(posthoc)
```

**Expected result:** Fail to reject H0. Volume-adjusted win rates do not differ significantly across volume groups. Low-volume, medium-volume, and high-volume outlets all win at approximately the same rate per unit of proxy volume.

**Visualization:** Side-by-side boxplots of win_rate across the three volume groups. If the boxes overlap substantially, volume explains the difference.

---

#### 4.3 Two-Way ANOVA: Volume Group x Outlet Type Interaction

**IS630 Session 6:** Two-Way ANOVA with interaction term

**Question:** Do both volume group and outlet type affect win rates, and do they interact?

**Setup:**
- Factor A: Volume group (Low / Medium / High) -- 3 levels
- Factor B: Outlet type (Branch / Authorised Retailer / Betting Centre) -- 3 levels (collapse small categories)
- Response: win_rate (wins per proxy unit)

**Hypotheses (three simultaneous tests):**
- H0a: Mean win rate is equal across all volume groups
- H0b: Mean win rate is equal across all outlet types
- H0c: There is no interaction between volume group and outlet type

```python
from statsmodels.formula.api import ols
import statsmodels.api as sm

model = ols('win_rate ~ volume_group + outlet_type + volume_group:outlet_type',
            data=df_residential).fit()
anova_table = sm.stats.anova_lm(model)
print(anova_table)

# Check ANOVA assumptions
residuals = model.resid
stat, p = stats.shapiro(residuals)
print(f"Shapiro-Wilk on residuals: p={p:.3f}")
```

**Interpretation:**
- If the interaction term (volume_group:outlet_type) is not significant (p > 0.05), the two factors act independently
- If outlet_type is significant, some outlet types inherently produce more winners per volume (could be due to system bet prevalence, not luck)
- If volume_group is not significant after controlling for outlet type, volume is the sole driver

---

#### 4.4 Welch's t-test / Mann-Whitney U: "Reputed Lucky" vs Others

**IS630 Session 5:** Two-sample t-test, Mann-Whitney U, Confidence Intervals

**Question:** Do outlets that are publicly reputed as "lucky" (media mentions) have higher volume-adjusted win rates than other outlets?

**Setup:**
- Group A: "Reputed lucky" outlets (manually identified from media, ~10-15 outlets: Delisia Agency, Tong Aik Huat, etc.)
- Group B: All other residential outlets (~240 outlets)
- Response: win_rate (volume-adjusted)

**Step 1: Check normality**
```python
stat_a, p_a = stats.shapiro(lucky['win_rate'])
stat_b, p_b = stats.shapiro(others['win_rate'])
```

*If normal:*
```python
# Welch's t-test (Session 5 -- does NOT assume equal variance)
t_stat, p_val = stats.ttest_ind(lucky['win_rate'], others['win_rate'], equal_var=False)
print(f"Welch's t-test: t={t_stat:.3f}, p={p_val:.5f}")

# 95% CI for difference in means (Session 4)
ci = stats.ttest_ind(lucky['win_rate'], others['win_rate'],
                     equal_var=False).confidence_interval(0.95)
print(f"95% CI for difference: [{ci.low:.4f}, {ci.high:.4f}]")
```

*If non-normal:*
```python
# Mann-Whitney U (Session 5 non-parametric)
u_stat, p_val = stats.mannwhitneyu(lucky['win_rate'], others['win_rate'],
                                    alternative='two-sided')
print(f"Mann-Whitney U: U={u_stat:.1f}, p={p_val:.5f}")
```

**Expected result:** No significant difference. "Reputed lucky" outlets have volume-adjusted win rates statistically indistinguishable from other outlets. The confidence interval for the difference in means should include zero.

**Visualization:** Boxplot comparing the two groups; annotate individual "famous" outlets on the plot.

---

#### 4.5 Confidence Intervals: Identifying Genuine Outliers

**IS630 Session 4:** Confidence Intervals

**Question:** After accounting for volume, does ANY individual outlet have a win count that is statistically significantly above expected?

**Setup:**
- For each outlet, compute the expected number of wins: E_i = total_wins x (v_i / sum(v_i))
- Compute a 95% confidence interval for the true win count using the Poisson distribution (since wins are count data)
- Apply **Bonferroni correction** for multiple comparisons (testing ~250 residential outlets means alpha_adjusted = 0.05 / 250 = 0.0002)

```python
# For each outlet, test whether observed wins significantly exceed expected
alpha_bonferroni = 0.05 / n_outlets
outlier_outlets = []

for i, row in outlet_summary.iterrows():
    observed = row['group1_wins']
    expected = row['expected_wins']

    # Poisson test: P(X >= observed | lambda = expected)
    p_val = stats.poisson.sf(observed - 1, mu=expected)  # P(X >= observed)

    if p_val < alpha_bonferroni:
        outlier_outlets.append({
            'outlet': row['outlet_name'],
            'observed': observed,
            'expected': round(expected, 1),
            'p_value': p_val
        })

# Also compute Poisson CI for each outlet's true rate
for i, row in outlet_summary.iterrows():
    # 95% CI using the exact Poisson interval
    lower = stats.chi2.ppf(0.025, 2 * row['group1_wins']) / 2 if row['group1_wins'] > 0 else 0
    upper = stats.chi2.ppf(0.975, 2 * (row['group1_wins'] + 1)) / 2
    # Does this CI exclude the expected value?
```

**Expected result:** After Bonferroni correction, 0-1 outlets (out of ~250) will have significantly elevated win counts. This is consistent with pure chance (at alpha = 0.05 with 250 tests, we expect 0.05 x 250 = 12.5 false positives without correction; with Bonferroni, we expect ~0).

**Deliverable:** A table of the top 10 "luckiest" outlets with their observed wins, expected wins, Poisson p-value, and whether they pass the Bonferroni threshold. The finding that none (or at most one) passes the threshold is the single most powerful result of the entire project.

---

### Phase 5: Regression Modeling

**IS630 Session:** 7 (Modeling Relationships: Linear Regression Models)

**Goal:** Quantify exactly how much of the variation in outlet wins is explained by volume (and other measurable features), and test whether any outlet characteristics predict "excess" wins beyond what volume alone explains.

This phase provides what Phase 4 cannot: a single number (R-squared) that says *"X% of the variation in wins is explained by volume."* This is the most direct and powerful answer to the project's central question.

#### 5.1 Simple Linear Regression: Wins ~ Volume

**Question:** How much of the variation in outlet win counts is explained by the volume proxy alone?

```python
from statsmodels.formula.api import ols
import statsmodels.api as sm

# Simple linear regression on residential outlets
model_simple = ols('group1_wins ~ proxy_volume_1000m', data=df_residential).fit()
print(model_simple.summary())
```

**Key outputs to report:**
- **R-squared:** The proportion of variance in wins explained by volume. If R-squared = 0.60, then 60% of the "luck" variation is just volume.
- **Slope (beta_1):** For every additional 1,000 HDB dwelling units near an outlet, wins increase by beta_1.
- **p-value of slope:** Is the relationship statistically significant?
- **Intercept (beta_0):** Expected wins for an outlet with zero nearby HDB units (interpret cautiously -- extrapolation).

**Assumptions to check (Session 7):**
```python
import matplotlib.pyplot as plt

# 1. Linearity: residuals vs fitted
plt.scatter(model_simple.fittedvalues, model_simple.resid)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Fitted values')
plt.ylabel('Residuals')
plt.title('Residuals vs Fitted')
plt.show()

# 2. Normality of residuals
stats.shapiro(model_simple.resid)
stats.probplot(model_simple.resid, dist="norm", plot=plt)

# 3. Homoscedasticity (constant variance of residuals)
# Visual check from residual plot above

# 4. Independence (not a concern here -- outlets are independent)
```

**Visualization:** Scatter plot with the regression line overlaid. Annotate famous "lucky" outlets -- visually, do they lie above the line (genuinely lucky) or on it (just high volume)?

**Expected result:** R-squared of 0.40-0.70. Volume explains a large share of the variance, but the exact value is an empirical finding. Outlets that appear "lucky" in raw counts will mostly lie near the regression line once volume is accounted for.

#### 5.2 Multiple Linear Regression: Wins ~ Volume + Outlet Type + Region

**Question:** After controlling for volume, do outlet type or region add any explanatory power?

```python
# Multiple regression with additional predictors
model_multi = ols('group1_wins ~ proxy_volume_1000m + outlet_type + region',
                  data=df_residential).fit()
print(model_multi.summary())

# Compare R-squared: does adding outlet_type and region improve the model?
print(f"Simple R-sq:   {model_simple.rsquared:.4f}")
print(f"Multiple R-sq: {model_multi.rsquared:.4f}")
print(f"Improvement:   {model_multi.rsquared - model_simple.rsquared:.4f}")
```

**Key outputs:**
- **Change in R-squared:** If adding outlet_type and region barely improves R-squared (e.g., from 0.55 to 0.57), volume is the dominant explanator.
- **Coefficient of outlet_type:** Do Betting Centres win more per unit volume than Authorised Retailers? (Possible, due to system bet prevalence.)
- **Coefficient of region:** After controlling for volume, does Central region still have higher wins? (If not, the "lucky neighborhood" effect is purely volume.)
- **Adjusted R-squared:** Penalizes for adding unhelpful predictors.

**Interpretation for the project narrative:** If the simple model (volume only) captures nearly as much variance as the multiple model, then volume alone is sufficient to explain outlet win patterns. "Luck" adds nothing.

#### 5.3 Residual Analysis: Who Are the True Outliers?

The regression residuals (observed wins minus predicted wins) are the **volume-adjusted excess wins**. Outlets with large positive residuals win more than their volume predicts.

```python
# Extract residuals and identify outliers
df_residential['predicted_wins'] = model_simple.fittedvalues
df_residential['residual'] = model_simple.resid
df_residential['std_residual'] = model_simple.resid / model_simple.resid.std()

# Outlets with standardized residuals > 2 (or > 3)
outliers = df_residential[df_residential['std_residual'] > 2].sort_values('std_residual', ascending=False)
print(f"Outlets with std residual > 2: {len(outliers)} out of {len(df_residential)}")
print(outliers[['outlet_name', 'group1_wins', 'predicted_wins', 'std_residual']])
```

**Expected result:** Very few outlets (0-5) have standardized residuals > 2. The "famous" outlets (Tong Aik Huat, Delisia Agency) will likely have residuals near zero once volume is controlled -- they win a lot because they sell a lot.

**Deliverable:** A ranked table of outlets by regression residual. This is the most compelling artifact in the entire project: the public's "luckiest" outlets, shown to be exactly as lucky as their volume predicts.

#### 5.4 PCA for Composite Predictor (Optional Extension)

**IS630 Session 8:** Dimensionality Reduction, PCA

If you have multiple correlated proxy features per outlet (HDB units at 500m, 750m, 1000m, 1500m; distance to MRT; number of nearby competitors), these predictors will be highly collinear. PCA can reduce them to a single composite "foot traffic accessibility" score.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Features: proxy volumes at different radii + other outlet characteristics
features = df_residential[['proxy_500m', 'proxy_750m', 'proxy_1000m', 'proxy_1500m']].values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

pca = PCA(n_components=2)
pcs = pca.fit_transform(features_scaled)

print(f"PC1 explains {pca.explained_variance_ratio_[0]:.1%} of variance")
print(f"PC2 explains {pca.explained_variance_ratio_[1]:.1%} of variance")
print(f"Loadings:\n{pd.DataFrame(pca.components_, columns=['500m','750m','1000m','1500m'], index=['PC1','PC2'])}")

# Use PC1 as composite volume predictor in regression
df_residential['volume_pc1'] = pcs[:, 0]
model_pca = ols('group1_wins ~ volume_pc1', data=df_residential).fit()
print(f"PCA regression R-sq: {model_pca.rsquared:.4f}")
```

**Why PCA fits here:** The four proxy radii measure the same underlying concept (foot traffic volume) but at different spatial scales. PC1 will likely capture 80-90% of the variance and serve as a cleaner single predictor than any one radius. This also resolves the "which radius is best?" question from Phase 2 by combining them all.

**Deliverable:** Scree plot showing variance explained by each PC; biplot or loading table; comparison of R-squared between single-radius and PCA-based regression.

---

### Phase 6: Bayesian Analysis

**IS630 Session:** 9 (Bayes' Theorem, Bayesian Modeling)

**Goal:** Apply Bayesian reasoning to answer the question from the opposite direction: instead of testing "is this outlet NOT random?" (frequentist), ask "given the data, what is our updated belief about this outlet's true win probability?" This provides a natural, intuitive framework for the "lucky outlet" question.

#### 6.1 Bayes' Theorem Applied to Outlet Luck

**Conceptual Setup:**

For each outlet, we want to estimate its true win probability theta_i. Using Bayes' Theorem:

```
P(theta_i | data) = P(data | theta_i) * P(theta_i) / P(data)
  posterior        =  likelihood      * prior       / evidence
```

- **Prior:** Before seeing any data, we assume all outlets have the same win probability. Use a weakly informative Beta prior: Beta(alpha_0, beta_0) centered on the overall win rate.
- **Likelihood:** The number of wins follows a Binomial (or Poisson) distribution given the outlet's true rate and volume.
- **Posterior:** After observing the data, each outlet's estimated probability is updated -- outlets with more wins get a slightly higher posterior, but the prior pulls extreme values toward the mean (shrinkage).

#### 6.2 Beta-Binomial Model

```python
from scipy import stats
import numpy as np

# Overall win rate across all residential outlets
total_wins = df_residential['group1_wins'].sum()
total_volume = df_residential['proxy_volume_1000m'].sum()
overall_rate = total_wins / total_volume

# Weakly informative prior: Beta(2, 2000)
# Centered near overall_rate, but with enough spread to be updated by data
alpha_prior = 2
beta_prior = int(alpha_prior / overall_rate) - alpha_prior

for i, row in df_residential.iterrows():
    wins_i = row['group1_wins']
    volume_i = row['proxy_volume_1000m']

    # Posterior: Beta(alpha_prior + wins, beta_prior + volume - wins)
    alpha_post = alpha_prior + wins_i
    beta_post = beta_prior + volume_i - wins_i

    # Posterior mean (shrinkage estimate)
    posterior_mean = alpha_post / (alpha_post + beta_post)

    # 95% Credible Interval
    ci_low = stats.beta.ppf(0.025, alpha_post, beta_post)
    ci_high = stats.beta.ppf(0.975, alpha_post, beta_post)

    # Does the credible interval exclude the overall rate?
    is_outlier = ci_low > overall_rate  # outlet is "luckier" than average
```

#### 6.3 Bayesian Shrinkage: The Key Insight

The most powerful Bayesian result is **shrinkage**: outlets with few tickets sold (small volume) get pulled strongly toward the overall average, while outlets with many tickets (large volume) are allowed to deviate more. This naturally handles the small-sample problem that plagues frequentist tests on low-volume outlets.

```python
# Compare raw rate vs Bayesian posterior mean
df_residential['raw_rate'] = df_residential['group1_wins'] / df_residential['proxy_volume_1000m']
df_residential['bayesian_rate'] = df_residential.apply(
    lambda r: (alpha_prior + r['group1_wins']) /
              (alpha_prior + beta_prior + r['proxy_volume_1000m']),
    axis=1
)

# Visualization: shrinkage plot
plt.scatter(df_residential['raw_rate'], df_residential['bayesian_rate'],
            alpha=0.5, s=df_residential['proxy_volume_1000m'] / 100)
plt.plot([0, df_residential['raw_rate'].max()],
         [0, df_residential['raw_rate'].max()], 'r--', label='No shrinkage')
plt.axhline(y=overall_rate, color='gray', linestyle=':', label='Overall rate')
plt.xlabel('Raw win rate (frequentist)')
plt.ylabel('Bayesian posterior mean')
plt.title('Bayesian Shrinkage: Low-volume outlets pulled toward mean')
plt.legend()
plt.show()
```

**Interpretation:** The shrinkage plot is the second "money chart" of the project (alongside the Phase 7 raw-vs-adjusted comparison). It shows that:
- High-volume outlets: raw rate and Bayesian rate are similar (lots of data, prior doesn't matter much)
- Low-volume outlets: Bayesian rate is pulled toward the overall average (little data, prior dominates)
- The "luckiest" outlets by raw rate are almost all low-volume outlets whose extreme rates are noise

#### 6.4 Posterior Comparison: "Reputed Lucky" vs Others

Use the posterior distributions to directly compare the "reputed lucky" group (from Phase 4.4) against all others:

```python
# P(lucky_outlet_rate > other_outlet_rate) via Monte Carlo sampling
lucky_posterior_samples = stats.beta.rvs(
    alpha_prior + lucky_total_wins,
    beta_prior + lucky_total_volume - lucky_total_wins,
    size=10000
)
other_posterior_samples = stats.beta.rvs(
    alpha_prior + other_total_wins,
    beta_prior + other_total_volume - other_total_wins,
    size=10000
)
prob_lucky_higher = np.mean(lucky_posterior_samples > other_posterior_samples)
print(f"P('lucky' outlets have higher rate) = {prob_lucky_higher:.3f}")
```

**Expected result:** P is close to 0.50 (no evidence that "lucky" outlets have a genuinely higher rate). This is the Bayesian counterpart to the frequentist t-test in Phase 4.4, and the convergence of both approaches strengthens the conclusion.

**Deliverable:** Shrinkage plot, table of posterior means and 95% credible intervals for top outlets, and the posterior probability comparison.

---

### Phase 7: Synthesis, Robustness, and the "Before vs After" Narrative

**IS630 Sessions:** 4-9 (all testing, regression, and Bayesian concepts)

**Goal:** Bring everything together with the most compelling visualization and robustness checks.

#### 7.1 The Raw vs Adjusted Comparison (The Money Chart)

This is the single most impactful visualization in the project. Show two side-by-side analyses:

**Left panel: Raw data (no volume adjustment)**
- Kruskal-Wallis test on raw win counts across 3 density groups
- Expected result: Highly significant (p << 0.05). High-density outlets win more.
- Boxplot showing clear separation between groups

**Right panel: Volume-adjusted data**
- Kruskal-Wallis test on win_rate (wins / proxy_volume) across same 3 groups
- Expected result: Not significant (p > 0.05). After adjusting for volume, groups are equal.
- Boxplot showing overlapping distributions

The contrast between the two panels is the story of the entire project: the "lucky outlet" myth is fully explained by volume.

```python
# Raw comparison
h_raw, p_raw = stats.kruskal(
    low_raw_wins, med_raw_wins, high_raw_wins
)

# Volume-adjusted comparison
h_adj, p_adj = stats.kruskal(
    low_adj_rate, med_adj_rate, high_adj_rate
)

print(f"Raw wins:     Kruskal-Wallis H={h_raw:.3f}, p={p_raw:.6f}")
print(f"Adjusted:     Kruskal-Wallis H={h_adj:.3f}, p={p_adj:.6f}")
```

#### 7.2 The Three Lenses Summary

Present the central finding through all three statistical paradigms taught in IS630:

| Approach | Test | Finding |
|---|---|---|
| **Frequentist (Sessions 4-6)** | ANOVA/Kruskal-Wallis, t-test, CI, Chi-Square | Volume-adjusted win rates show no significant difference across groups; no individual outlet passes Bonferroni-corrected outlier detection |
| **Regression (Session 7)** | Simple & Multiple Linear Regression | R-squared of X% -- volume explains the vast majority of win variation; regression residuals show no systematically "lucky" outlets |
| **Bayesian (Session 9)** | Beta-Binomial posterior, shrinkage | Posterior credible intervals for all outlets overlap the overall rate; shrinkage pulls apparent outliers toward the mean |

The convergence of all three approaches on the same conclusion -- **volume, not luck** -- is far more convincing than any single test.

#### 7.3 Sensitivity Analysis

Run all Phase 4-5 tests at four proxy radii (500m, 750m, 1000m, 1500m) and report whether conclusions change:

| Test | r=500m | r=750m | r=1000m | r=1500m |
|---|---|---|---|---|
| 4.1 Chi-Square Independence | p=? | p=? | p=? | p=? |
| 4.2 Kruskal-Wallis | p=? | p=? | p=? | p=? |
| 4.4 Mann-Whitney U | p=? | p=? | p=? | p=? |
| 5.1 Simple Regression R-sq | R²=? | R²=? | R²=? | R²=? |

If conclusions are stable across radii, the analysis is robust to proxy specification. If they flip, discuss which radius is most defensible and why. Alternatively, report results using the PCA composite predictor (Phase 5.4) which sidesteps this issue entirely.

#### 7.4 Group 1 vs Combined Analysis

Report all Phase 4-6 results for both:
- **Group 1 only** (conceptually cleaner: jackpot wins only)
- **Group 1 + Group 2 combined** (more statistical power: ~5x more data)

This is a built-in robustness check. If both analyses converge on the same conclusion, the finding is strong.

#### 7.5 Commercial Outlet Sub-Analysis

Repeat the Kruskal-Wallis test (4.2), regression (5.1), and Bayesian analysis (6.2) for commercial-area outlets separately. Explicitly note that the HDB proxy is unreliable for these outlets and that any apparent significance may be driven by proxy error, not luck.

---

## Thread-to-IS630 Session Mapping

| Phase | Test | IS630 Session | Technique | Python Function |
|---|---|---|---|---|
| 1 | Descriptive stats | Sessions 1-2 | Mean, median, std, IQR, skewness | `np.mean`, `np.std`, `pd.describe` |
| 1 | Correlation | Session 2 | Spearman rank correlation | `stats.spearmanr` |
| 3 | Poisson fit | Session 3 | Distribution fitting, PMF | `stats.poisson.pmf`, `stats.chisquare` |
| 4.1 | Chi-Square Independence | **Session 6** | Contingency table, standardized residuals | `chi2_contingency` |
| 4.2 | Assumption checks | **Sessions 5-6** | Shapiro-Wilk, Levene's test | `stats.shapiro`, `stats.levene` |
| 4.2 | One-Way ANOVA | **Session 6** | F-test, post-hoc comparisons | `f_oneway`, `pairwise_tukeyhsd` |
| 4.2 | Kruskal-Wallis | **Session 6** | Non-parametric multi-group comparison | `stats.kruskal`, `sp.posthoc_dunn` |
| 4.3 | Two-Way ANOVA | **Session 6** | Interaction effects | `ols`, `sm.stats.anova_lm` |
| 4.4 | Welch's t-test | **Session 5** | Two-sample comparison (unequal variance) | `stats.ttest_ind(equal_var=False)` |
| 4.4 | Mann-Whitney U | **Session 5** | Non-parametric two-sample comparison | `stats.mannwhitneyu` |
| 4.5 | Confidence intervals | **Session 4** | Poisson CI, Bonferroni correction | `stats.chi2.ppf`, `stats.t.interval` |
| 5.1 | Simple Linear Regression | **Session 7** | OLS, R-squared, residual analysis | `ols`, `model.summary()` |
| 5.2 | Multiple Linear Regression | **Session 7** | Multiple predictors, adjusted R-sq | `ols`, `model.summary()` |
| 5.3 | Residual analysis | **Session 7** | Standardized residuals, outlier detection | `model.resid`, scatter plots |
| 5.4 | PCA | **Session 8** | Dimensionality reduction, composite predictor | `sklearn.decomposition.PCA` |
| 6.2 | Beta-Binomial model | **Session 9** | Bayesian updating, posterior distribution | `stats.beta.ppf`, `stats.beta.rvs` |
| 6.3 | Bayesian shrinkage | **Session 9** | Prior-posterior comparison | `stats.beta`, scatter plot |
| 7.1 | Before/after comparison | **Session 6** | Kruskal-Wallis (raw vs adjusted) | `stats.kruskal` |

Every major IS630 technique across all 9 teaching sessions is now represented: descriptive statistics, distributions, confidence intervals, z/t-tests, Welch's t-test, Mann-Whitney U, ANOVA (one-way and two-way), Kruskal-Wallis, Dunn's test, Tukey HSD, Chi-Square Test of Independence, Shapiro-Wilk, Levene's test, **simple and multiple linear regression**, **PCA**, and **Bayesian modeling with Beta-Binomial posteriors**.

---

## Member Assignment Suggestion

| Member | Phase | Primary IS630 Technique | Deliverable |
|---|---|---|---|
| A | Phase 1: EDA + Phase 2: Proxy | Descriptive stats, correlation, data visualization | EDA report, proxy validation, choropleth maps |
| B | Phase 3: Distribution Analysis | Poisson fitting, chi-squared GOF | Distribution fit report, dispersion analysis |
| C | Phase 4.1 + 4.3: Chi-Square + Two-Way ANOVA | Chi-Square Independence, Two-Way ANOVA | Region analysis, interaction effects |
| D | Phase 4.2 + 4.4 + 4.5: Hypothesis Tests | One-Way ANOVA, Kruskal-Wallis, Welch's t-test, CIs | Central tests: win rates across groups, outlier detection |
| E | Phase 5: Regression + Phase 5.4: PCA | Simple & Multiple Linear Regression, PCA | R-squared analysis, residual outlier table, PCA composite predictor |
| F | Phase 6: Bayesian + Phase 7: Synthesis | Bayesian Beta-Binomial, shrinkage, robustness | Posterior analysis, shrinkage plot, sensitivity tables, "three lenses" summary |

---

## What Was Dropped and Why

| Dropped Thread | Reason | Replacement |
|---|---|---|
| **Moran's I / LISA** | Not covered in IS630; specialized spatial statistics requiring libpysal | Chi-Square Test of Independence on region x win category (Phase 4.1) -- tests the same "lucky neighborhood" question using Session 6 material |
| **Wald-Wolfowitz Runs Test** | Not covered in IS630; data sparsity makes per-outlet runs tests meaningless (1-2 wins per 1,200 draws) | Addressed qualitatively in the discussion section citing hot-hand literature (Gilovich et al., 1985) |
| **Equal-lambda Poisson** (straw-man) | Trivially rejected because outlets have different volumes; proves nothing about luck | Volume-stratified Poisson check (Phase 3.1 Test B) -- tests whether within-group variation exceeds Poisson expectation |
| **Monte Carlo chi-squared** | Monte Carlo simulation not explicitly taught as an examinable technique in IS630 | Standard chi-squared GOF with cell collapsing when expected counts are small |

**Restored from original proposal:**

| Restored Thread | Reason | Phase |
|---|---|---|
| **Bayesian Beta-Binomial** | Session 9 covers Bayes' Theorem and Bayesian Modeling -- this is legitimate IS630 content. Reformulated with proper prior specification and shrinkage analysis. | Phase 6 |

---

## Key Methodological Improvements

1. **Full IS630 coverage (Sessions 1-9).** The methodology now uses every major technique taught across all 9 sessions, including linear regression (Session 7), PCA (Session 8), and Bayesian modeling (Session 9). This directly addresses the rubric criterion "Understanding and application of statistical concepts."

2. **Three statistical paradigms.** The same core question ("does volume explain wins?") is answered using frequentist hypothesis testing (Phase 4), regression modeling (Phase 5), and Bayesian analysis (Phase 6). Convergence across all three is far more convincing than any single approach.

3. **Proxy-first design.** The volume proxy is validated before any hypothesis test, not treated as an afterthought. Known failure modes (commercial areas) are explicitly handled through subgroup analysis.

4. **Assumption checking at every step.** Every parametric test is preceded by Shapiro-Wilk (normality) and Levene's (equal variance). If assumptions fail, the non-parametric alternative (Kruskal-Wallis instead of ANOVA, Mann-Whitney U instead of t-test) is used. This directly demonstrates IS630 Session 5-6 decision-tree thinking.

5. **Coherent narrative flow.** Instead of six disconnected threads, the analysis tells a story: describe the data (Phase 1), validate the tool (Phase 2), characterize the pattern (Phase 3), test the hypothesis (Phase 4), model the relationship (Phase 5), apply Bayesian reasoning (Phase 6), synthesize with compelling before-vs-after and three-paradigm comparisons (Phase 7).

6. **Regression as the centerpiece.** The simple linear regression R-squared is the single most interpretable number in the entire project. "Volume explains X% of win variation" is something any audience immediately understands. The regression residual table provides the definitive answer to "which outlets are genuinely lucky?"

7. **Bayesian shrinkage as the closer.** The shrinkage plot provides an intuitive visual demonstration that apparent "luck" in low-volume outlets is statistical noise. This is the Bayesian way of saying what Bonferroni correction says frequentistically -- small samples produce extreme values.

8. **Robustness through replication.** The same core question is tested using multiple methods across multiple data slices (Group 1 only, combined, residential only, all outlets) and proxy specifications (4 radii + PCA composite). Convergence across all these is far more convincing than a single test.
