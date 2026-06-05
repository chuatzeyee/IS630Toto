# IS630 Group Project — Idea Proposals

**Prepared by:** [Your Name]
**Date:** 10 May 2026
**Course:** IS630 Statistical Thinking in Data Science, AY2025 Apr

---

## Context

The project requires us to define a real-world problem and answer analytical questions using frequentist and/or Bayesian statistical techniques. It accounts for 30% of the final grade. The rubric values **innovative use of data**, **deeper analytical questions**, exploration of **counter-intuitive results**, and a clear **"So what?"** for decision-making.

Below are three project ideas, each designed to go beyond surface-level analysis by framing a counter-intuitive hypothesis, segmenting by meaningful subgroups, and leveraging the full statistical toolkit we learn across Sessions 1–9 (EDA, distributions, CLT, confidence intervals, hypothesis testing, ANOVA, regression, Bayesian inference).

---

## Idea 1: Beyond the Stars — Does Rating Inflation Make E-Commerce Reviews Statistically Meaningless?

### The Core Insight

Everyone trusts star ratings when shopping online. But average ratings have been steadily inflating — on most platforms, 90%+ of products sit between 4.0 and 5.0 stars. If nearly everything is "4.5 stars," does the rating system actually help consumers distinguish quality? This project investigates whether star ratings have become a broken signal.

### Why It's Novel

- **Counter-intuitive framing:** Ratings are designed to help consumers, but inflation may have rendered them useless — a paradox worth investigating statistically.
- **Not a standard Kaggle walkthrough:** Most student projects on e-commerce data predict sales or segment customers. Almost none examine the *statistical validity of the rating system itself*.
- **Real-world "So What?":** Direct implications for platform design (should platforms force-distribute ratings? use different scales?) and consumer decision-making.

### Analytical Questions

1. What distribution do product ratings actually follow? (Normal? J-shaped? Power law?) Does it differ by product category?
2. Is there statistically significant rating drift over time (inflation)?
3. Do products rated 4.2 vs 4.5 actually differ in objective quality proxies (return rate, complaint rate, delivery issues)?
4. Does the number of reviews moderate the reliability of the rating? (Bayesian angle — small-sample ratings are less trustworthy)
5. Can we identify "gaming" patterns — sellers whose ratings don't match delivery/quality metrics?

### Statistical Methods

| Method | Application |
|--------|-------------|
| Descriptive stats + EDA | Distribution shape of ratings, skewness analysis, Anscombe's Quartet-style warning |
| Distribution fitting | Test whether ratings follow Normal, Beta, or other distributions (KS test, Shapiro-Wilk) |
| Hypothesis testing | Two-sample t-tests comparing quality proxies across rating tiers; ANOVA across categories |
| Confidence intervals | CI for mean rating by category; CI for "inflation rate" over time |
| Regression | Multiple regression: what predicts actual satisfaction beyond the star rating? |
| Bayesian inference | Prior beliefs about product quality updated with review counts (small n → wide posterior, large n → narrow) |

### Dataset

**Brazilian E-Commerce Public Dataset (Olist)** on Kaggle — 100K+ orders with: order timestamps, product categories, seller IDs, review scores (1–5), review text, delivery dates, actual vs estimated delivery. The delivery data provides an *objective quality proxy* independent of subjective ratings.

Link: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

### Team Division (6 members)

1. EDA + distribution analysis of ratings
2. Time-series analysis of rating inflation
3. Hypothesis testing: ratings vs objective quality (delivery performance)
4. Category-level segmentation and ANOVA
5. Bayesian analysis of review reliability by sample size
6. Regression modeling + practical recommendations

---

## Idea 2: The Mood-Streaming Paradox — Does Sadder Music Actually Get More Plays?

### The Core Insight

Common sense says people prefer happy, upbeat music. But Spotify's own data tells a different story — some of the most-streamed tracks score low on "valence" (Spotify's measure of musical positivity). This project tests whether there's a statistically significant relationship between a song's emotional tone and its streaming success, and whether this varies by genre.

### Why It's Novel

- **Directly counter-intuitive:** Challenges the assumption that "feel-good = popular."
- **Multi-dimensional:** Valence is just one of ~13 audio features Spotify quantifies. The interaction between features (e.g., high energy + low valence = intense sadness vs mellow sadness) creates rich analytical space.
- **Cultural/genre angle:** You can segment by genre to see if mood preferences vary — e.g., do K-pop listeners prefer higher valence than indie rock listeners?
- **Nobody does this rigorously:** Most Spotify Kaggle projects just do basic EDA or build a recommender. Statistical *hypothesis testing* on mood vs popularity is rare.

### Analytical Questions

1. Is there a significant correlation between valence and stream count? Is it positive or negative?
2. Does the valence-popularity relationship differ across genres? (Interaction effect)
3. What combination of audio features (danceability, energy, valence, tempo, acousticness) best predicts streaming success? Are there surprising features that matter more than expected?
4. Has the "mood" of popular music shifted over the decades? (Test for temporal trend)
5. Do songs with extreme audio profiles (very sad OR very happy) outperform moderate ones? (Non-linear relationship)

### Statistical Methods

| Method | Application |
|--------|-------------|
| EDA + visualization | Scatter plots of valence vs popularity, distribution of audio features by genre |
| Distribution fitting | What distribution do stream counts follow? (Likely log-normal or power law, not normal) |
| Hypothesis testing | Compare mean valence of top-100 vs bottom-100 streamed songs; paired tests across genres |
| ANOVA | Compare audio feature means across genre groups |
| Correlation + regression | Multiple regression with audio features as predictors of log(streams) |
| Bayesian | Prior belief "happy songs stream more" — does the data update this toward the opposite? |
| CLT / CI | Confidence intervals for mean valence of "hit songs" vs "non-hits" |

### Datasets

**Primary (pick one):**

- **Spotify Tracks (GitHub, 600K tracks, 1922–2021)** — largest pre-collected dataset with all audio features + popularity. Direct CSV download, no account needed.
  Link: https://github.com/urvog/Spotify-Tracks
- **Spotify Tracks (HuggingFace, 114K tracks, 125 genres)** — same data as the popular Kaggle set but hosted on HuggingFace. No Kaggle account needed.
  Link: https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset

**Supplementary (for academic depth):**

- **P4KxSpotify (Zenodo, 18K albums)** — audio features matched to Pitchfork critic scores. CC BY 4.0 license, DOI-citable for references.
  Link: https://zenodo.org/records/3603330
- **MSSD — Music Streaming Sessions Dataset (AICrowd, 160M sessions)** — audio features + actual listening/skip behavior from Spotify Research. Published paper: arXiv:1901.09851. Free, requires AICrowd login.
  Link: https://www.aicrowd.com/challenges/spotify-sequential-skip-prediction-challenge/dataset_files

**Note:** Spotify deprecated its Audio Features API endpoint in Nov 2024, so fresh data collection is no longer possible. All datasets above were collected before the cutoff.

### Team Division (6 members)

1. EDA + audio feature distributions
2. Valence-popularity hypothesis testing (main question)
3. Genre-level segmentation + ANOVA
4. Temporal trend analysis (has popular music gotten sadder?)
5. Multi-feature regression modeling
6. Bayesian analysis + synthesis of findings and practical implications

---

## Idea 3: The Green Premium Illusion — Do ESG-Rated Companies Actually Deliver Better Returns, or Is It Just Marketing?

### The Core Insight

Environmental, Social, and Governance (ESG) investing has exploded — funds marketed as "sustainable" now manage trillions of dollars. The implicit promise is that "doing good" and "doing well" go hand-in-hand. But does the data actually support this? This project statistically tests whether ESG scores predict stock returns, and crucially, whether the relationship holds after controlling for sector, size, and market conditions.

### Why It's Novel

- **Extremely timely:** ESG investing is a hot-button issue in finance and policy. Some recent studies suggest the premium is illusory.
- **Counter-intuitive in *both* directions:** Some expect ESG = better returns (virtue is rewarded). Others expect ESG = worse returns (costly constraints). The truth may be "no significant difference" — which is itself a powerful finding.
- **Multi-layered:** The relationship likely varies by sector (ESG matters more in energy than tech?), time period (bull vs bear markets), and ESG dimension (E vs S vs G separately).
- **Not a standard portfolio project:** Most finance student projects predict stock prices. Testing the *statistical validity of an entire investment thesis* is much more intellectually ambitious.

### Analytical Questions

1. Is there a statistically significant difference in mean returns between high-ESG and low-ESG companies?
2. Does the ESG-return relationship vary by sector? (Interaction effect + ANOVA)
3. Do the E, S, and G pillars have different predictive power? (Which dimension actually matters?)
4. Is the ESG-return relationship robust after controlling for company size and sector? (Regression)
5. Do high-ESG companies show lower return *volatility* (risk), even if mean returns are similar? (Variance comparison using F-test)
6. Bayesian question: If our prior is "ESG helps returns," how much does 10 years of data shift that belief?

### Statistical Methods

| Method | Application |
|--------|-------------|
| EDA | Distribution of ESG scores across sectors, return distributions (test normality) |
| Hypothesis testing | Two-sample t-test: high-ESG vs low-ESG returns; F-test for variance comparison |
| ANOVA | Compare returns across ESG terciles/quartiles; across sectors |
| Confidence intervals | CI for mean return difference between ESG groups |
| Regression | Multiple regression: returns ~ ESG + sector + size + market condition |
| Bayesian inference | Update prior belief about ESG premium with observed data |
| Distribution fitting | Test whether returns are normally distributed (KS/Shapiro-Wilk) — important for test validity |

### Datasets

- **S&P 500 ESG Risk Ratings** on Kaggle — ESG scores for S&P 500 companies with sector, industry, and full company name
- **S&P 500 Stock Data** on Kaggle — Historical daily prices for all S&P 500 companies (can compute returns)
- Combine both by ticker/company name for the analysis period

Links:
- https://www.kaggle.com/datasets/pritish509/s-and-p-500-esg-risk-ratings
- https://www.kaggle.com/datasets/camnugent/sandp500

### Team Division (6 members)

1. EDA + ESG score distributions across sectors
2. Overall ESG-return hypothesis testing (main question)
3. Sector-level ANOVA and interaction analysis
4. E vs S vs G pillar decomposition
5. Risk/volatility analysis (variance comparison)
6. Bayesian analysis + regression + conclusions

---

## Comparison Matrix

| Criterion | Rating Inflation | Spotify Mood | ESG Returns |
|-----------|:---:|:---:|:---:|
| Novelty | High | High | Very High |
| Counter-intuitive angle | Strong | Strong | Strong |
| Dataset availability | Excellent (single dataset) | Excellent (single dataset) | Good (2 datasets, need merging) |
| Statistical depth | Very High | High | Very High |
| "So What?" factor | Strong (platform design) | Medium (music industry) | Very Strong (trillion-dollar industry) |
| Divisible for 6 people | Excellent | Excellent | Excellent |
| Medium article appeal | High | Very High (pop culture) | Very High (finance/policy) |
| Risk of thin results | Low | Low | Medium (null result is still publishable) |

---

## Recommendation

- **Maximum academic rigour + novelty:** ESG Returns — the most ambitious, multi-dataset, and the topic is genuinely debated in academic finance.
- **Most fun + highest Medium article virality:** Spotify Mood — the pop-culture hook is strong, the data is clean, and everyone can relate to music.
- **Safest path to a good grade with the richest single dataset:** Rating Inflation — the Olist dataset is incredibly rich (100K orders with objective quality proxies), and there's almost no risk of "no interesting findings."
