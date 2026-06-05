# IS630 Group Project Ideas — Comprehensive Evaluation

## Evaluation Framework

Each idea is assessed against the IS630 Project Requirements (30% of final grade) on seven criteria:

| Criterion | What It Measures | Weight |
|-----------|-----------------|--------|
| **Course Alignment** | Fit with frequentist/Bayesian statistical techniques (hypothesis tests, CIs, distributions) | Critical |
| **Data Availability** | Is the data downloadable, clean, and large enough for meaningful analysis? | Critical |
| **Novelty** | Does it offer a new perspective, counter-intuitive hypothesis, or original angle? | High |
| **Statistical Depth** | Can 6 people each apply distinct statistical methods? | High |
| **"So What?" Factor** | Does the conclusion matter to a real audience? | Medium |
| **Presentation Appeal** | Will it engage a non-specialist audience in 15 minutes? | Medium |
| **Risk Profile** | Probability of ending up with boring/null results or data roadblocks? | Medium |

---

## Idea 1: Singapore Weather vs Tourism

**Proposed by:** Teammate  
**Premise:** Test whether Singapore's climate comfort (temperature, humidity) correlates with tourist arrivals by country of origin.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| Tourist arrivals by country (monthly) | data.gov.sg | CSV | 13,700 rows x 4 cols (1978-2015) |
| Surface air temperature (monthly mean) | data.gov.sg | CSV | ~526 rows x 2 cols (1982-2025) |
| Relative humidity (monthly mean) | data.gov.sg | CSV | ~526 rows x 2 cols (1982-2025) |

### Difficulties & Risks

1. **Near-zero signal in the data.** Singapore is equatorial. Monthly mean temperature ranges from ~26.0C to ~28.5C year-round — a 2.5C band. Monthly humidity ranges from ~78% to ~86%. These fluctuations are tiny. Finding a statistically significant relationship between such minimal weather variation and tourism numbers is extremely unlikely.

2. **Confounders dwarf the weather signal.** Tourist arrivals are driven by school holidays (June, December spikes), major festivals (Chinese New Year, Deepavali), airline pricing, visa policies, economic conditions, exchange rates, marketing campaigns, and major events (F1, NDP). Weather is not even in the top 10 factors. Any correlation found is almost certainly spurious or driven by seasonality that happens to coincide with temperature cycles.

3. **Data ends in 2015.** The tourist arrivals dataset stops at November 2015 — a decade ago. The professor may question why you are studying pre-COVID tourism patterns with no path to current relevance. The SINGSTAT alternative extends to 2026 but requires significant reshaping from wide format.

4. **The "by country" angle lacks operationalizability.** The proposer suggests analyzing whether tourists from different countries react differently to Singapore's heat. This requires each source country's climate profile as an additional dataset — which was not identified. Even if obtained, the causal logic ("Norwegians are more deterred by heat than Malaysians") cannot be tested from aggregate monthly counts.

5. **Limited statistical variety.** With monthly data merged across three tiny datasets, the analysis boils down to: compute correlations, run a few regressions, maybe segment by region. It is difficult to fill 6 people's work with distinct statistical contributions.

### Statistical Methods Fit

| Method | Applicability | Issue |
|--------|--------------|-------|
| Correlation / Regression | Possible but likely non-significant | Weather variation too small |
| Hypothesis tests (t-test) | Hot months vs cool months arrivals | "Hot" and "cool" are barely distinguishable in Singapore |
| ANOVA by country group | Possible | But arrivals are driven by holidays, not weather |
| Time series decomposition | Good fit | But goes beyond course content (Sessions 1-5) |
| Confidence intervals | Thin application | Only for mean arrivals in weather bins |

### Verdict

**Rating: 3/10.** The fundamental problem is physics: Singapore's weather barely varies, so there is no meaningful signal to detect. You would spend weeks on data preparation only to conclude "weather has no significant effect on tourism in an equatorial city" — a result that is obvious without statistical analysis. The professor's tip to "go beyond simple descriptions" and "ask deeper questions" cannot be met when the data is inherently flat.

---

## Idea 2: Telecom Customer Churn

**Proposed by:** Teammate  
**Premise:** Examine whether different customer types exhibit different churn behaviour in telecommunications.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| IBM Telco Customer Churn (typical) | Kaggle | CSV | ~7,000 rows x 21 cols |

### Difficulties & Risks

1. **The single most overused project topic in data science.** Search "telecom churn" on Kaggle: 10,000+ notebooks. Search on Medium: thousands of articles. Every data science bootcamp, every introductory ML course, and every statistics class has seen this exact dataset and analysis. The professor has almost certainly evaluated multiple teams on this exact topic before.

2. **Novelty is nearly impossible.** The project requirements explicitly ask for "Context and Novelty" — explain how your work "builds on or differs from previous work." When thousands of analyses already exist for the same dataset, claiming novelty requires a genuinely unique angle that the proposer has not articulated.

3. **Classification-oriented, not statistics-oriented.** The natural analytical question ("Can we predict churn?") leads to logistic regression, decision trees, and random forests — machine learning, not statistical thinking. IS630 is about hypothesis testing, confidence intervals, probability distributions, and Bayesian inference. Force-fitting these tools onto a prediction problem feels unnatural and will show.

4. **The dataset is synthetic.** IBM created this dataset for demo purposes. There is no real company, no real customer base, no real business context. When the rubric asks "So what? Why does this matter to the company?", you are answering about a fictional entity.

5. **The proposer's angle is vague.** "How different types of customers respond differently" is what every churn analysis does. There is no specific counter-intuitive hypothesis, no surprising angle, no "I'm not sure if the data backs this up" moment that drives genuine inquiry.

### Statistical Methods Fit

| Method | Applicability | Issue |
|--------|--------------|-------|
| Chi-squared test | Churn by segment | Works, but basic |
| Two-sample t-test | Monthly charges: churners vs non-churners | Every analysis does this |
| Logistic regression | Prediction | More ML than stats-thinking |
| ANOVA | Tenure by contract type | Possible but not insightful |
| Confidence intervals | For churn rate by segment | Thin |

### Verdict

**Rating: 2/10.** This is the safest way to get an average grade and the surest way to not get a great one. The professor grades on "innovative use of data" and "understanding of statistical concepts in context." Submitting the most overused dataset in data science with generic segmentation analysis signals neither innovation nor deep thinking.

---

## Idea 3: ESG vs Stock Returns

**Proposed by:** Teammate  
**Premise:** Test whether companies with higher ESG scores deliver better stock returns. Break down E, S, G components. Run ANOVA across sectors. Compare returns AND volatility.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| S&P 500 ESG Risk Ratings | Kaggle | CSV | ~503 rows x 15 cols |
| S&P 500 historical stock prices | Kaggle / yfinance | CSV | ~1.3M rows x 8 cols |

### Difficulties & Risks

1. **The ESG dataset is tiny.** 503 rows — one row per company. This is a cross-sectional snapshot, not time series. After filtering out companies with missing ESG scores, you may have ~450 rows. For sector-level ANOVA, some sectors will have fewer than 30 companies, reducing statistical power.

2. **Data merge is non-trivial.** ESG ratings are a point-in-time snapshot. Stock returns are daily time series. You need to decide: which time period of returns corresponds to the ESG rating? 1 year? 3 years? 5 years? The choice materially affects results, and there is no objectively correct answer.

3. **Survivorship bias is a serious methodological issue.** The S&P 500 index reconstitutes quarterly. Companies that performed poorly and were removed from the index are not in the current ESG dataset. This biases the sample toward successful companies and undermines any causal interpretation.

4. **Extensive prior research.** Friede, Busch & Bassen (2015) conducted a meta-analysis of 2,200+ studies on ESG and financial performance. The academic literature is enormous. Claiming novelty against this body of work is very challenging.

5. **Likely null result.** As the proposer acknowledged, the most probable finding is "no significant difference." While a null result can be framed as valuable ("the market does not reward ESG"), it makes for a less compelling 15-minute presentation and requires sophisticated argumentation to avoid sounding like "we found nothing."

6. **Confounders require multivariate regression.** Returns depend on sector, market cap, beta, momentum, interest rates, etc. Simple two-sample tests (high ESG vs low ESG returns) are confounded. Proper analysis requires multiple regression with controls — which may or may not be covered in Sessions 6-9.

### Statistical Methods Fit

| Method | Applicability | Issue |
|--------|--------------|-------|
| Two-sample t-test | High vs Low ESG returns | Confounded without controls |
| ANOVA | Returns by ESG quintile, by sector | Good fit — strongest method here |
| Confidence intervals | Mean return difference | Good fit |
| Regression | Return ~ ESG + sector + size | If covered in later sessions |
| Variance comparison (F-test) | ESG companies less volatile? | Nice angle |
| Bayesian comparison | Prior/posterior on ESG premium | If covered in later sessions |

### Verdict

**Rating: 5/10.** The statistical methods are a good fit for the course, and the E/S/G decomposition plus volatility angle adds depth. But the tiny cross-sectional dataset (503 rows), complex merge requirements, survivorship bias, and vast prior literature make this risky. If you can navigate the data prep and frame the analysis carefully, it can work — but it demands more data engineering than statistical thinking.

---

## Idea 4: Spotify — Does Sadder Music Get More Plays?

**Proposed by:** Teammate  
**Premise:** Test whether lower-valence (sadder-sounding) songs get more streams. Segment by genre. Check temporal trends. Explore non-linear effects.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| Spotify Tracks | HuggingFace / Kaggle | CSV | 114,000 rows x 20 cols |

Also available via Google Drive link shared by proposer.

### Difficulties & Risks

1. **Valence is not the same as sadness.** Spotify's "valence" measures musical positivity of the *sound* — tempo, key, timbre. It does not capture lyrics. A fast-tempo minor-key song about heartbreak could have medium valence. The construct validity of "valence = sadness" should be acknowledged as a limitation, not treated as fact.

2. **"Popularity" is not stream count.** The dataset contains a `popularity` score (0-100), not actual stream numbers. Spotify's popularity metric heavily weights recency: a 1990s classic with 2 billion streams may score lower than a new release with 50 million streams. This distorts any analysis of whether sadder music is more popular *overall*.

3. **Confounders.** A song's popularity is driven by playlist placement, label marketing spend, viral social media moments, artist fame, and release timing. Audio features like valence explain only a fraction of the variance. Expect low R-squared values in regression.

4. **Selection bias.** The 114K tracks are a sample of Spotify's 100M+ track catalog. How was the sample drawn? If it overrepresents popular or Western music, genre-level conclusions are biased.

5. **Genre segmentation reduces power.** The dataset has 125 genres. Splitting 114K tracks across 125 genres gives ~900 per genre on average, but distribution is uneven. Niche genres may have too few tracks for meaningful hypothesis tests.

### Why It Works Despite the Difficulties

1. **114,000 rows with 16 numeric features.** This is by far the largest, cleanest, most feature-rich dataset among all proposals. Every statistical method in the course can be applied meaningfully.

2. **Multiple independent, testable hypotheses:**
   - H1: Songs with lower valence have higher popularity (two-sample t-test, CI for difference)
   - H2: The valence-popularity relationship varies by genre (ANOVA, post-hoc tests)
   - H3: Pop music has gotten sadder over decades (temporal trend analysis)
   - H4: Extreme moods (very happy OR very sad) outperform middle-valence songs (non-linear test)
   - H5: Different audio features (danceability, energy, acousticness) moderate the valence effect
   - H6: Explicit-content songs have different valence distributions (chi-squared, t-test)

3. **Natural 6-way work split.** Each member can own a different hypothesis or a different audio feature analysis while using shared data preparation.

4. **Strongest "So what?" in entertainment context.** Results have implications for record labels (what to produce), playlist curators (what to recommend), and artists (what sounds resonate). The audience can relate personally.

5. **Excellent presentation potential.** You can embed actual song examples: "This song scores 0.12 valence and has 2.3 billion streams. This song scores 0.95 valence and has 200 million streams. Are sad songs systematically more popular?" This kind of concrete storytelling is what the rubric means by "captivating, innovative, and engaging."

6. **Counter-intuitive premise.** The rubric tip says "if results seem counter-intuitive, investigate why they might be true." The entire premise — people *prefer* sad music? — is built on this.

### Statistical Methods Fit

| Method | Applicability | Quality of Fit |
|--------|--------------|---------------|
| Two-sample t-test | Low-valence vs high-valence popularity | Excellent |
| ANOVA / Kruskal-Wallis | Popularity across valence quartiles, across genres | Excellent |
| Confidence intervals | Mean popularity difference by valence group | Excellent |
| Chi-squared | Is valence independent of genre? Explicit flag? | Excellent |
| Correlation + regression | Popularity ~ valence + energy + danceability + ... | Excellent |
| Bayesian comparison | Prior belief (happy = popular) vs posterior | Good if covered |
| Non-parametric tests | If popularity is heavily skewed (it will be) | Excellent |
| Normality tests | Shapiro-Wilk on popularity distributions by group | Excellent |
| Effect size (Cohen's d) | Practical significance of valence-popularity gap | Excellent |

### Verdict

**Rating: 8.5/10.** The best overall choice. The dataset is large, clean, and feature-rich. The premise is counter-intuitive and relatable. Every statistical method in the course can be applied naturally. The difficulties (valence != sadness, popularity != streams) are real but can be framed as honest limitations rather than fatal flaws — the rubric rewards critical reflection. Six team members can each own a distinct analytical thread. The presentation will practically write itself with real song examples.

---

## Idea 5: Speed Dating — What Makes Someone Go On a Second Date?

**Proposed by:** Teammate  
**Premise:** Analyze what attributes predict a match in speed dating. Compare self-perception vs others' perception.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| Speed Dating Experiment | Kaggle | CSV | 8,378 rows x 195 cols |

### Difficulties & Risks

1. **Severely missing data.** Many columns have structural missing values (participants did not complete all survey waves). Some columns are 65%+ missing. Extensive imputation or column-dropping is required before any analysis, consuming significant project time on data prep rather than statistical thinking.

2. **Small and culturally narrow sample.** 552 participants from Columbia University, NYC, 2002-2004. The demographics skew young, educated, and American. Generalizing findings to other populations (e.g., Singapore) is indefensible.

3. **Famous, well-analyzed dataset.** This is from the published paper by Fisman & Iyengar (2006, *Quarterly Journal of Economics*). Hundreds of analyses exist on Kaggle and in coursework. Novelty is hard to claim.

4. **The proposer called it "unserious."** For a 30% final grade at the master's level, this framing could hurt. The rubric asks for "practical implications" and "recommendations to the audience." Who is the audience for "what makes a speed date successful"? What decision-maker benefits?

5. **195 columns create analysis paralysis.** With 195 features, the temptation is to test everything. Without disciplined hypothesis framing, the analysis becomes a fishing expedition that produces spurious significant results (multiple comparisons problem).

6. **Class imbalance.** 6,998 non-matches vs 1,380 matches (16.5% match rate). This makes naive statistical comparisons misleading.

### Statistical Methods Fit

| Method | Applicability | Issue |
|--------|--------------|-------|
| Two-sample t-test | Do men vs women rate attractiveness differently? | Good, but well-trodden |
| Paired t-test | Self-rating vs partner's rating | Good angle |
| Chi-squared | Is matching independent of race/field? | Good |
| ANOVA | Rating scores across demographic groups | Good |
| Logistic regression | Predict match | ML-leaning |
| Confidence intervals | Proportion who match by group | Thin |

### Verdict

**Rating: 5/10.** The dataset has genuine statistical richness, and the self-perception vs. others' perception angle is interesting. But the missing data burden, small culturally-specific sample, lack of novelty, and the "unserious" positioning all work against it. It would make a fun presentation, but the professor's rubric emphasizes "understanding of statistical concepts in context" and "quality of evidence-based insights" — both are undermined by the data quality issues and narrow generalizability.

---

## Idea 6: Diversification — Always Good?

**Proposed by:** Teammate  
**Premise:** Test whether diversification always leads to higher alpha. Find overlapping assets. Chart optimal number of stocks.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| Not specified | — | — | — |

### Difficulties & Risks

1. **No dataset was identified.** The proposer did not specify where the data comes from. Constructing a proper portfolio dataset with daily returns, sector classifications, and correlation matrices for 500 stocks is a substantial data engineering project in itself.

2. **This is finance theory, not statistical analysis.** The efficient frontier, diminishing returns of diversification, and optimal portfolio size are results from Modern Portfolio Theory (Markowitz, 1952). You would essentially be re-deriving 70-year-old theory, not performing novel statistical analysis.

3. **"Alpha" requires factor models.** Computing alpha (excess return over a benchmark after adjusting for risk) requires CAPM or Fama-French factor models. These are specialized financial econometrics, not the hypothesis testing and confidence intervals taught in IS630.

4. **Unfocused scope.** The proposal combines three distinct questions: (a) does diversification help? (b) are some portfolios falsely diversified due to overlapping assets? (c) what is the optimal number of stocks? Each could be a separate project. Trying all three guarantees none is done well.

5. **The "overlapping assets" point is trivial.** Noting that SPY and QQQ overlap by ~70% is a correlation matrix computation, not a hypothesis test. It takes one line of code and one paragraph to explain.

### Statistical Methods Fit

| Method | Applicability | Issue |
|--------|--------------|-------|
| Simulation | Generate portfolios of different sizes | Not a statistical test |
| Correlation matrix | Asset overlap | Descriptive, not inferential |
| Hypothesis test | ??? | No clear testable hypothesis |
| Confidence intervals | ??? | For what parameter? |

### Verdict

**Rating: 2/10.** The weakest proposal. No dataset, no testable hypothesis, no alignment with course methods. It is a finance simulation exercise disguised as a statistics project. The rubric cannot be satisfied when there is no clear analytical question to test with statistical techniques.

---

## Idea 7: Dividends = Higher Growth?

**Proposed by:** Same teammate as Diversification  
**Premise:** Compare total returns of dividend-paying vs non-dividend-paying S&P 500 stocks.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| S&P 500 stock prices | Kaggle / yfinance | CSV | ~1.3M rows x 8 cols |
| Dividend information | Not clearly specified | — | — |

### Difficulties & Risks

1. **Well-trodden territory.** Dividend investing vs growth investing is one of the most debated topics in retail finance. Vanguard, Morningstar, and dozens of finance academics have published extensive analyses. Novelty is very limited.

2. **One main test.** The core analysis is a two-sample t-test: mean total return of dividend stocks vs non-dividend stocks. After that, what? Segmenting by sector adds a few more tests, but the overall statistical depth is shallow for 6 people.

3. **Time period cherry-picking.** Results depend heavily on the time window. Dividend stocks outperformed in 2000-2010 (tech crash + financial crisis favored value). Growth stocks dominated 2010-2020 (tech boom). Any conclusion is contingent on the chosen period, which the proposer has not addressed.

4. **Survivorship bias.** Companies that went bankrupt and stopped paying dividends are not in the current S&P 500 dataset. This biases the dividend portfolio's returns upward.

5. **Dividend data is not in the stock price dataset.** To classify stocks as dividend-paying vs non-dividend, you need a separate dividend history dataset. The proposer did not identify one.

6. **Limited course alignment.** The interesting questions in dividend investing (risk-adjusted returns, Sharpe ratios, drawdown analysis) require finance-specific methodology beyond the course scope.

### Statistical Methods Fit

| Method | Applicability | Issue |
|--------|--------------|-------|
| Two-sample t-test | Dividend vs non-dividend returns | One test, then what? |
| ANOVA | Returns by dividend yield quartile | Possible |
| F-test / Levene's test | Volatility comparison | Good but thin |
| Confidence interval | Difference in mean returns | One computation |
| Regression | Return ~ dividend_flag + sector | If covered |

### Verdict

**Rating: 3/10.** Too thin for a 6-person team. One main hypothesis test, no clearly identified dividend dataset, heavy time period dependency, and well-explored territory. It could work as a sub-section of a larger finance project but not as a standalone project.

---

## Idea 8: Singapore Pools — Are There "Lucky" Outlets?

**Proposed by:** Teammate  
**Premise:** Test whether some TOTO outlets are statistically "luckier" than others, controlling for tickets sold, footfall, operating history, and demographics.

### Datasets

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| TOTO winning outlets (Group 1 & 2) | Singapore Pools website | Web scraping required | ~300 outlets x 3-4 cols |
| Outlet details (location, hours) | Singapore Pools website | Web scraping required | ~300 outlets x 5-6 cols |
| Census 2020 demographics | singstat.gov.sg | Downloadable | By planning area |

### Difficulties & Risks

1. **Data scraping is required.** The winning outlets page uses a SharePoint-based dynamic loading mechanism. There is no CSV download. You need Selenium/Playwright to scrape it. This adds technical complexity and potential Terms of Service concerns. Several GitHub projects have done this (e.g., mapattacker/toto), but for a statistics course, the time spent on web scraping is time not spent on statistical analysis.

2. **Very small dataset.** After scraping, you have ~300 outlets with win frequencies. Many outlets will have zero or one Group 1/2 wins. The data is extremely sparse for formal hypothesis testing.

3. **"Tickets sold per outlet" is not public.** This is the critical confounding variable — outlets that sell more tickets will have more winners, by pure probability. Without volume data, you cannot properly test whether any outlet is genuinely "lucky." Footfall data is similarly unavailable.

4. **The answer is statistically predetermined.** Lottery outcomes are independent random events. After controlling for volume (if you had it), the remaining variation is sampling noise. The conclusion will be "no, there are no lucky outlets" — which is correct but not surprising.

5. **Rare event statistics require careful handling.** Win counts per outlet follow a Poisson distribution with very low lambda. Chi-squared goodness-of-fit tests have low power with many zero-count cells. You may need exact tests or Bayesian approaches, which adds complexity.

### Why It Partially Works

1. **Highest novelty.** No team in IS630 history has likely analyzed Singapore Pools data. It is locally relevant, quirky, and immediately engaging.

2. **Perfect "So what?"** — literally debunking a common Singaporean superstition. The audience at SMU will relate instantly.

3. **Geospatial visualization.** Mapping winning outlets onto Singapore's planning areas, overlaying with demographics — this makes for a visually striking presentation.

4. **Good Poisson distribution fit.** Session 3 covers Poisson distributions. Testing whether wins follow a Poisson process across outlets is a direct application of course material.

5. **Bayesian angle.** Prior belief ("some outlets are lucky") vs posterior after seeing the data. This is a textbook application of Bayesian updating that the professor would appreciate.

### Statistical Methods Fit

| Method | Applicability | Quality of Fit |
|--------|--------------|---------------|
| Chi-squared goodness of fit | Are wins uniformly distributed? | Good (if enough data) |
| Poisson model | Wins per outlet ~ Poisson(lambda) | Excellent — course Session 3 |
| Hypothesis test | Is outlet win rate > expected? | Good |
| Bayesian updating | Prior (lucky outlets exist) to posterior | Excellent if covered |
| Geospatial clustering | Are winners geographically clustered? | Visual, not formal |
| Confidence intervals | For win rate per region | Good |

### Verdict

**Rating: 6/10.** The most novel and locally compelling idea, but data availability is the critical risk. If the team can scrape the data and there are enough observations (100+ wins), it could produce a memorable, distinctive project. If the scrape fails or the data is too sparse, the project collapses. High reward, high risk.

---

## Comparative Ranking (Summary Scores)

| Criterion | Weather-Tourism | Telecom Churn | ESG Returns | Spotify | Speed Dating | Diversification | Dividends | SG Pools |
|-----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **Course Alignment** | 4 | 3 | 6 | 9 | 6 | 2 | 4 | 7 |
| **Data Availability** | 5 | 8 | 5 | 10 | 5 | 1 | 4 | 3 |
| **Novelty** | 4 | 1 | 4 | 7 | 3 | 3 | 2 | 10 |
| **Statistical Depth** | 3 | 3 | 6 | 9 | 6 | 2 | 3 | 5 |
| **"So What?" Factor** | 3 | 4 | 5 | 7 | 3 | 4 | 4 | 9 |
| **Presentation Appeal** | 4 | 3 | 5 | 9 | 8 | 3 | 3 | 8 |
| **Low Risk** | 3 | 6 | 4 | 7 | 5 | 2 | 4 | 4 |
| **Overall Score (/70)** | **26** | **28** | **35** | **58** | **36** | **17** | **24** | **46** |
| **Rating** | 3/10 | 2/10 | 5/10 | **8.5/10** | 5/10 | 2/10 | 3/10 | 6/10 |

---

## Annotated Scoring Matrix

### Course Alignment — Fit with hypothesis tests, CIs, distributions, Bayesian methods

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 4 | Correlation and regression possible but near-zero weather variation means tests will be non-significant. Time series decomposition fits better but is beyond Sessions 1-5. |
| Telecom Churn | 3 | Natural framing is classification/prediction (logistic regression, decision trees) — ML, not statistical thinking. Hypothesis tests can be forced in but feel unnatural. |
| ESG Returns | 6 | ANOVA across ESG quintiles, t-tests for high vs low ESG, F-test for volatility all fit well. Loses points because proper analysis needs multivariate regression to control confounders. |
| **Spotify** | **9** | Every course method applies naturally: t-tests (sad vs happy), ANOVA (across genres), CIs (popularity differences), chi-squared (valence vs genre independence), non-parametric tests (skewed popularity), Bayesian A/B test. |
| Speed Dating | 6 | Two-sample t-tests (gender differences), paired t-tests (self vs other ratings), chi-squared (matching vs demographics), ANOVA (ratings by career) all apply. Loses points for 195 columns inviting p-hacking. |
| Diversification | 2 | No clear hypothesis to test. The analysis is simulation-based (generate random portfolios), not inferential statistics. Alpha computation needs factor models outside course scope. |
| Dividends | 4 | One clean two-sample t-test (dividend vs growth returns). ANOVA by yield quartile is possible. But the statistical work is thin — one main test, then what? |
| SG Pools | 7 | Poisson goodness-of-fit is a direct Session 3 application. Chi-squared test for uniform distribution of wins. Bayesian prior/posterior on "lucky outlets." Loses points because sparse data may limit test power. |

### Data Availability — Downloadable, clean, large enough, no scraping or complex merges

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 5 | All three CSVs are freely downloadable from data.gov.sg. But the datasets are tiny (~526 rows each), require merging on date, and tourist arrivals end in 2015 — a decade stale. |
| Telecom Churn | 8 | IBM Telco dataset is a one-click Kaggle download, ~7K rows, clean, no missing values, no merge needed. Scores high on convenience but the data is synthetic. |
| ESG Returns | 5 | ESG ratings CSV is available (503 rows) and stock prices are downloadable. But merging a point-in-time snapshot with daily time series is non-trivial and introduces methodological choices that affect results. |
| **Spotify** | **10** | Single CSV download from HuggingFace, 114K rows x 20 columns, clean, no merge required. By far the largest and most analysis-ready dataset of all proposals. |
| Speed Dating | 5 | One CSV from Kaggle, 8.4K rows. But 195 columns with some 65%+ missing requires extensive cleaning and imputation — substantial prep time before any analysis begins. |
| Diversification | 1 | No dataset was identified by the proposer. Building a portfolio simulation dataset from scratch is a data engineering project, not readily available for download. |
| Dividends | 4 | Stock price data is available on Kaggle/yfinance. But dividend classification data (which stocks pay dividends, how much, when) was not identified — a critical gap. |
| SG Pools | 3 | Winning outlet data requires web scraping from a SharePoint-based site with dynamic "Load More" loading. Census data is downloadable but must be geo-matched to outlet locations. Result is ~300 rows — very small. |

### Novelty — New perspective, counter-intuitive hypothesis, original angle

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 4 | Weather-tourism studies exist in academic literature. The Singapore-specific angle adds mild novelty, but the equatorial constraint makes the question uninteresting: the answer is known before testing. |
| Telecom Churn | 1 | The least novel idea possible. 10,000+ Kaggle notebooks, thousands of Medium articles, every data science bootcamp uses this dataset. The professor has almost certainly seen this multiple times. |
| ESG Returns | 4 | ESG-returns is heavily researched (2,200+ studies in one meta-analysis alone). The E/S/G decomposition angle adds some novelty, but the question itself is well-trodden. |
| **Spotify** | **7** | The counter-intuitive premise ("people prefer sad music?") is genuinely engaging. Genre segmentation, temporal trends in mood, and non-linear effects add original angles. Not a 10 because Spotify analyses exist — but this specific hypothesis framing is distinctive. |
| Speed Dating | 3 | Famous dataset from a 2006 published paper (Fisman & Iyengar). Hundreds of analyses on Kaggle. The self-perception vs others' angle is mildly novel but not enough to overcome the dataset's fame. |
| Diversification | 3 | The efficient frontier and diversification benefits are 70-year-old finance theory (Markowitz 1952). The overlapping-assets angle is a factoid, not a novel hypothesis. |
| Dividends | 2 | Dividend vs growth is one of the most debated, most analyzed topics in retail investing. Vanguard, Morningstar, and dozens of academics have published extensively. |
| **SG Pools** | **10** | The most novel idea by far. No IS630 team (and likely no academic paper) has analyzed Singapore Pools outlet data this way. Locally relevant, quirky, immediately engaging. Perfect score for originality. |

### Statistical Depth — Can 6 people each apply distinct statistical methods?

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 3 | After computing correlations and running a regression, there is little left. The merged dataset is tiny (~400 monthly observations). Segmenting by region stretches it, but 6 distinct analytical threads are hard to fill. |
| Telecom Churn | 3 | EDA, segmentation, chi-squared, t-test on charges, logistic regression — that's 5 steps but they form a linear pipeline, not 6 independent analyses. Most are prerequisite for the next. |
| ESG Returns | 6 | Overall test, E/S/G decomposition, sector ANOVA, volatility F-test, and Bayesian comparison give 5-6 distinct threads. Loses points because the 503-row cross-section limits per-sector sample sizes. |
| **Spotify** | **9** | 6+ fully independent hypotheses: valence-popularity (t-test), genre segmentation (ANOVA), temporal trends, multi-feature regression, explicit content (chi-squared), Bayesian comparison. Each is a standalone analysis on 114K rows. |
| Speed Dating | 6 | Gender differences, self vs other perception, match predictors, demographic effects, and rating dynamics give 5 threads. Loses points because 65% missing data means some threads may collapse after cleaning. |
| Diversification | 2 | Simulation, correlation matrix, and a variance decay curve are the only outputs. None are formal hypothesis tests. Hard to give 6 people distinct inferential statistics work. |
| Dividends | 3 | One main t-test (dividend vs growth returns), one ANOVA (by yield quartile), one F-test (volatility). That's 3 tests — half the team has no statistical deliverable. |
| SG Pools | 5 | Poisson model, chi-squared test, Bayesian updating, and demographic analysis give 4 threads. Geospatial mapping adds a fifth (visual, not statistical). The sixth member is stretched. |

### "So What?" Factor — Does the conclusion matter to a real audience?

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 3 | Who acts on the finding that "Singapore's weather doesn't affect tourism"? The Singapore Tourism Board already knows this. No actionable insight for any decision-maker. |
| Telecom Churn | 4 | Retention strategies are relevant to telcos, but the dataset is synthetic (IBM demo data). Recommendations go to a fictional company. The "So what?" is generic and ungrounded. |
| ESG Returns | 5 | Relevant to investors, fund managers, and ESG advocates. But a null result ("no significant difference") has muted impact. The E/S/G decomposition adds value if one component matters. |
| **Spotify** | **7** | Implications for record labels (what to produce), playlist curators (what to recommend), and artists (what resonates). Every audience member personally listens to music, making the "So what?" visceral. |
| Speed Dating | 3 | Who benefits from knowing what makes a 4-minute speed date successful? No decision-maker, no policy implication. The proposer's own "unserious" label reflects this weakness. |
| Diversification | 4 | Relevant to retail investors, but the conclusion (diversification has diminishing returns) is textbook knowledge. No new "So what?" emerges from re-deriving known theory. |
| Dividends | 4 | Relevant to retail investors, but the answer depends on time period and is already well-established by Vanguard/Morningstar research. Limited marginal insight. |
| **SG Pools** | **9** | Directly debunks a common Singaporean superstition. The audience at SMU will relate instantly — many have bought TOTO. The "So what?" is visceral: "Should you queue at that 'lucky' outlet?" Every Singaporean has an opinion. |

### Presentation Appeal — Will it engage a non-specialist audience in 15 minutes?

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 4 | Temperature charts and tourist arrival graphs are visually bland. The equatorial flatness of the data makes for unexciting visualizations. Hard to build a narrative arc. |
| Telecom Churn | 3 | Generic business problem with no emotional hook. Churn rate by contract type doesn't captivate. The audience has seen this before in other courses. |
| ESG Returns | 5 | Topical (ESG investing is trendy) and can spark debate. But financial charts and ANOVA tables are dry. The null result scenario makes for an anticlimactic climax. |
| **Spotify** | **9** | Embed actual songs: "This #1 hit scores 0.08 valence. This upbeat track only got 200K streams." The audience recognizes songs, debates whether they're really "sad," and has personal stakes. Best storytelling potential of any idea. |
| Speed Dating | 8 | Inherently entertaining — "what do men vs women actually care about?" sparks engagement. The "unserious" nature that hurts grading rigor actually helps presentation energy. |
| Diversification | 3 | Efficient frontier plots and correlation matrices are finance-class material, not captivating storytelling. Niche audience appeal. |
| Dividends | 3 | Returns comparison charts are standard finance fare. No emotional hook, no surprise moment, no audience participation angle. |
| SG Pools | 8 | Open with "Which of you has bought TOTO at a 'lucky' outlet?" — instant audience engagement. Map visualization of winning outlets is visually striking. Myth-debunking narrative arc is compelling. |

### Low Risk — Low probability of boring/null results or data roadblocks

| Idea | Score | Justification |
|------|:-----:|---------------|
| Weather-Tourism | 3 | Very high risk of null results. Singapore's 2.5C temperature range almost guarantees non-significance. If the main hypothesis fails, there is no fallback — the data has no other interesting dimension. |
| Telecom Churn | 6 | Low risk of data problems (clean synthetic dataset). But the risk of a generic, unremarkable analysis is high. You will get results — they just won't be interesting or novel. |
| ESG Returns | 4 | Medium-high risk. The likely null result on ESG-returns is acknowledged by the proposer. Data merge complexity could consume weeks. Survivorship bias undermines any causal claim. |
| **Spotify** | **7** | Low risk. Even if the primary hypothesis (sad = more popular) fails, there are 10+ other audio features and 125 genres to explore. The dataset is guaranteed clean and large. Worst case: you find "valence doesn't matter, but danceability does" — still interesting. |
| Speed Dating | 5 | Medium risk. The 65% missing data could eliminate planned analyses. If key columns are too sparse after cleaning, you may lose entire analytical threads. Small sample (552 participants) limits statistical power. |
| Diversification | 2 | Very high risk. No dataset means the project can't even start without first building the data pipeline. The simulation approach may not satisfy the rubric's demand for hypothesis testing. |
| Dividends | 4 | Medium risk. Time period dependency means results could flip based on the chosen window. The thin analysis (one main test) means there's little to fall back on if the conclusion is "it depends on when you look." |
| SG Pools | 4 | High risk on data acquisition — the scrape may fail or produce too few observations. If only 50 Group 1 wins exist, formal hypothesis tests lack power. The predetermined "no lucky outlets" answer limits surprise value. |

---

## Recommendation: Spotify Is the Clear Best Choice

**The Spotify idea wins on nearly every dimension.** Here is why:

### Why Spotify over SG Pools (the second-best)?

| Factor | Spotify | SG Pools |
|--------|---------|----------|
| Data ready today? | Yes — one CSV download, 114K rows | No — needs scraping, ~300 rows |
| Statistical depth for 6 people? | 6+ independent hypotheses, 10+ features | 2-3 tests on sparse data |
| Risk of project failure? | Low — data is guaranteed clean | High — scrape may fail or data too sparse |
| Fallback if primary hypothesis fails? | Many other features to explore | Limited fallback options |

### Why Spotify over ESG/Speed Dating (tied third)?

- **ESG** has good statistical depth but the dataset is tiny (503 rows), merge is complex, and survivorship bias undermines validity.
- **Speed Dating** has rich data but 65%+ missing values in some columns, it is culturally narrow, and the "unserious" positioning is a grading risk.
- **Spotify** has none of these problems: 114K clean rows, no merge required, globally relatable.

### Key Recommendations If Spotify Is Chosen

1. **Acknowledge valence != sadness upfront.** Frame it as "musical positivity" or "sonic mood" rather than claiming it measures sadness. This shows critical thinking.
2. **Acknowledge popularity != streams.** Explain Spotify's recency-weighted algorithm. Suggest "stream count" as future work.
3. **Pre-register your hypotheses.** State all hypotheses before running tests. This prevents accusations of p-hacking and demonstrates methodological rigor.
4. **Use real song examples in the presentation.** Nothing engages an audience like recognizing "that song I listen to every day scores 0.08 valence."
5. **Combine frequentist AND Bayesian.** Run a Bayesian A/B test comparing sad vs happy song popularity alongside the frequentist t-test. This directly satisfies the rubric requirement for "combination of techniques from one or both philosophies."

---

## Work Split by Idea (6 Team Members)

### Spotify (Recommended)

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Project Lead + Data Prep** | Data cleaning, feature engineering, train/test split, shared notebook setup | Clean dataset, data dictionary, EDA summary, missing value treatment |
| **M2: Valence-Popularity Analysis** | Core hypothesis — does lower valence correlate with higher popularity? | Two-sample t-test, Mann-Whitney U, confidence intervals, effect size (Cohen's d), scatter plots |
| **M3: Genre Segmentation** | Does the valence-popularity relationship differ by genre? | One-way ANOVA / Kruskal-Wallis across genres, post-hoc tests, genre-level CIs |
| **M4: Temporal Trends** | Has music gotten sadder over the decades? | Time series of mean valence by release year, trend tests, popularity evolution |
| **M5: Multi-Feature Analysis** | Beyond valence — which audio features best predict popularity? | Multiple regression, correlation matrix, feature importance, interaction effects |
| **M6: Bayesian Analysis + Synthesis** | Bayesian comparison of sad vs happy music, overall conclusion | Bayesian A/B test, prior specification, posterior credible intervals, final report/article editing |

### Singapore Weather vs Tourism

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Integration** | Merge tourism, temperature, humidity datasets; handle date alignment | Merged dataset, time series alignment |
| **M2: Overall Correlation** | Temperature/humidity vs total arrivals | Correlation tests, scatter plots, regression |
| **M3: Regional Segmentation** | Segment by tourist source region (ASEAN, East Asia, Europe, etc.) | ANOVA by region, CIs per region |
| **M4: Seasonal Decomposition** | Separate seasonal patterns from weather effects | Decomposition, detrending |
| **M5: Country Climate Profiles** | Source country climate data, compute "climate gap" | External data sourcing, differential analysis |
| **M6: Report + Presentation** | Write-up, visualization, literature review | Slides, report/Medium article |

### Telecom Customer Churn

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Prep + EDA** | Clean data, feature engineering, EDA | Summary statistics, distributions, missing value handling |
| **M2: Segment Profiling** | Define customer segments (tenure, contract, usage) | Clustering or rule-based segmentation, profiles |
| **M3: Hypothesis Testing** | Do churners have higher monthly charges? More support calls? | t-tests, chi-squared, CIs |
| **M4: Segment-Level Analysis** | Churn rate varies by segment? | ANOVA, post-hoc, segment-level CIs |
| **M5: Predictive Analysis** | Which factors predict churn? | Logistic regression or similar |
| **M6: Recommendations + Report** | Business implications, retention strategies | Write-up, slides, cost-benefit analysis |

### ESG vs Stock Returns

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Merge + Cleaning** | Merge ESG ratings with stock returns, handle survivorship | Merged dataset, return calculations |
| **M2: Overall ESG-Returns Test** | High ESG vs Low ESG total returns | Two-sample t-test, CI, effect size |
| **M3: E/S/G Decomposition** | Which component matters most? | Separate tests for E, S, G scores; ANOVA |
| **M4: Sector Analysis** | Does ESG matter more in energy than tech? | ANOVA by sector, interaction analysis |
| **M5: Volatility Analysis** | Are ESG companies less risky? | F-test, Levene's test, variance comparison |
| **M6: Bayesian + Report** | Bayesian prior/posterior on ESG premium, write-up | Bayesian analysis, report, slides |

### Speed Dating

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Cleaning** | Handle 195 columns, impute missing values, select relevant features | Clean dataset, feature selection rationale |
| **M2: Gender Differences** | Do men and women value different attributes? | t-tests on rating dimensions by gender |
| **M3: Self vs Other Perception** | Does self-rating match how others rate you? | Paired t-tests, correlation, gap analysis |
| **M4: Match Predictors** | Which attributes predict a match? | Logistic regression, chi-squared |
| **M5: Demographic Effects** | Does race, age, or career field affect matching? | ANOVA, chi-squared independence |
| **M6: Report + Presentation** | Story framing, visualization, write-up | Slides, report, literature review |

### Diversification

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Sourcing + Portfolio Construction** | Download S&P 500 returns, build random portfolios | Portfolio simulation framework |
| **M2: Risk-Return Frontier** | Compute efficient frontier for different portfolio sizes | Simulation results, frontier plots |
| **M3: Overlap Analysis** | Correlation between major ETFs and index components | Correlation matrices, heatmaps |
| **M4: Optimal N Analysis** | At what N does diversification benefit plateau? | Simulation, variance decay curve |
| **M5: Sector Diversification** | Within-sector vs cross-sector diversification | Sector-level analysis |
| **M6: Report + Presentation** | Write-up, recommendations | Slides, report |

### Dividends vs Growth

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Prep** | Classify S&P 500 into dividend/non-dividend, compute total returns | Clean dataset, classification logic |
| **M2: Total Return Comparison** | Two-sample t-test: dividend vs growth total returns | Hypothesis test, CI, effect size |
| **M3: Sector Segmentation** | Does the dividend effect vary by sector? | ANOVA, sector-level CIs |
| **M4: Time Period Analysis** | Bull market vs bear market performance | Subperiod analysis, structural break tests |
| **M5: Volatility Comparison** | Dividend stocks less volatile? | F-test, Levene's, drawdown analysis |
| **M6: Report + Presentation** | Recommendations, write-up | Slides, report |

### Singapore Pools

| Member | Role | Key Deliverables |
|--------|------|-----------------|
| **M1: Data Scraping + Cleaning** | Scrape winning outlets, outlet details from Singapore Pools | Structured dataset, scraping scripts |
| **M2: Descriptive Analysis + Mapping** | Geospatial visualization, outlet distribution | Maps, frequency distributions, EDA |
| **M3: Poisson Analysis** | Do wins follow a Poisson distribution? Goodness-of-fit test | Chi-squared test, Poisson model fit |
| **M4: Demographic Overlay** | Merge with Census 2020 planning area data | Demographic profiles, correlation with win rates |
| **M5: Bayesian Lucky Outlet Test** | Prior (lucky outlets exist) vs posterior | Bayesian inference, credible intervals |
| **M6: Report + Presentation** | Narrative framing (debunking myths), write-up | Slides, report, "So what?" framing |

---

## Final Summary

| Rank | Idea | Score | One-Line Reason |
|------|------|-------|----------------|
| 1 | **Spotify** | 8.5/10 | Largest clean dataset, most hypotheses, best course fit, universally relatable |
| 2 | **SG Pools** | 6/10 | Most novel and locally compelling, but data scraping and sparsity are serious risks |
| 3 | **Speed Dating** | 5/10 | Rich multi-attribute data but 65% missing values, old, culturally narrow, "unserious" |
| 4 | **ESG Returns** | 5/10 | Good statistical depth but tiny cross-section (503 rows), complex merge, prior literature |
| 5 | **Weather-Tourism** | 3/10 | Near-zero weather variation in equatorial Singapore — no signal to detect |
| 6 | **Dividends** | 3/10 | One main t-test, well-trodden, no specified dataset |
| 7 | **Telecom Churn** | 2/10 | Most overused dataset in data science, misaligned with statistical thinking course |
| 8 | **Diversification** | 2/10 | No dataset, no testable hypothesis, finance theory exercise not stats project |

**Go with Spotify.** It is the only idea that simultaneously satisfies all seven evaluation criteria at a high level. The difficulties are manageable limitations to disclose, not project-killing flaws.
