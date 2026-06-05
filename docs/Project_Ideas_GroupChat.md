Hey all, here are a few ideas from my side. I tried to think of angles that are a bit different from the typical Kaggle project — each one has a counter-intuitive hook and enough statistical depth for the full toolkit we'll cover (EDA, hypothesis testing, ANOVA, regression, Bayesian, etc.). Happy to discuss any of these or mix and match.

---

**Idea 1: Beyond the Stars — Does Rating Inflation Make E-Commerce Reviews Statistically Meaningless?**

We all rely on star ratings when shopping online, but have you noticed that almost everything is rated 4+ stars these days? If 90% of products sit between 4.0 and 5.0, does the rating system actually help us distinguish good products from bad ones? The idea here is to statistically test whether star ratings have become a broken signal.

What makes this interesting is that we wouldn't just look at ratings in isolation — we'd compare them against objective quality proxies like delivery performance (did the product arrive on time? was there a complaint?). We could also test whether ratings have drifted upward over time (inflation), whether the number of reviews affects how trustworthy a rating is (Bayesian angle), and whether some sellers are gaming the system (high stars but poor delivery metrics).

The dataset I'm looking at is the Brazilian E-Commerce (Olist) dataset on Kaggle — it has 100K+ orders with review scores, delivery timestamps, product categories, and seller data. It's rich enough for all of us to take a different cut: someone does EDA on rating distributions, someone tests inflation over time, someone does ANOVA across product categories, someone runs the Bayesian reliability analysis, and so on.

Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

**Idea 2: The Mood-Streaming Paradox — Does Sadder Music Actually Get More Plays?**

Common sense says people prefer happy, upbeat music. But some of the most-streamed songs on Spotify score really low on "valence" — Spotify's measure of how positive or cheerful a song sounds. So the question is: is there actually a statistically significant relationship between a song's emotional tone and how many streams it gets? And does this vary by genre?

This is more interesting than just "what makes a hit song" because we'd be testing a specific counter-intuitive hypothesis. We could segment by genre (do pop listeners prefer happier music than indie rock listeners?), look at whether popular music has gotten sadder over the decades, and check for non-linear effects (maybe extreme moods — very happy OR very sad — outperform the middle ground). Spotify provides ~13 audio features per track (danceability, energy, tempo, acousticness, etc.), so there's plenty to work with for regression and ANOVA.

For datasets, there are a few good options that don't require Kaggle. The biggest one is on GitHub (urvog/Spotify-Tracks) with ~600K tracks from 1922–2021, all audio features included — just download the CSV directly. There's also the same 114K-track dataset mirrored on HuggingFace if you prefer a smaller, cleaner set. For extra academic rigour, there's a Zenodo dataset (P4KxSpotify) that matches Spotify audio features to Pitchfork critic scores — it has a DOI we can cite properly. And if we really want to go deep, Spotify Research released the MSSD (Music Streaming Sessions Dataset) with 160M listening sessions and skip behaviour, published in an academic paper.

Note: Spotify killed their Audio Features API in late 2024, so we can't collect fresh data, but all the above were scraped before the cutoff.

Datasets:
- GitHub (600K tracks): https://github.com/urvog/Spotify-Tracks
- HuggingFace (114K tracks): https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset
- Zenodo P4KxSpotify (18K albums, DOI-citable): https://zenodo.org/records/3603330
- AICrowd MSSD (160M sessions, academic paper): https://www.aicrowd.com/challenges/spotify-sequential-skip-prediction-challenge/dataset_files

---

**Idea 3: The Green Premium Illusion — Do ESG-Rated Companies Actually Deliver Better Stock Returns?**

ESG (Environmental, Social, Governance) investing is massive right now — trillions of dollars are in funds marketed as "sustainable." The pitch is that doing good and doing well go hand-in-hand. But does the data actually back this up? This project would statistically test whether companies with higher ESG scores actually deliver better stock returns, and whether that holds up once you control for sector and company size.

What I like about this one is that it's counter-intuitive in both directions. Some people assume ESG = better returns (virtue is rewarded by the market). Others assume ESG = worse returns (sustainability constraints are costly). The truth might be "no significant difference" — and that null result is itself a powerful finding with real implications for the investment industry.

We could break the E, S, and G pillars apart to see which one actually matters (maybe governance predicts returns but environmental doesn't?), run ANOVA across sectors (does ESG matter more in energy than in tech?), and compare not just returns but also volatility — maybe ESG companies don't earn more, but they're less risky (lower variance in returns).

This one needs two datasets merged: the S&P 500 ESG Risk Ratings dataset and the S&P 500 historical stock price data, both on Kaggle. A bit more data prep work, but the payoff is a genuinely ambitious analysis.

Datasets:
- https://www.kaggle.com/datasets/pritish509/s-and-p-500-esg-risk-ratings
- https://www.kaggle.com/datasets/camnugent/sandp500

---

My personal ranking: ESG is the most ambitious and novel (finance professors would find this genuinely interesting). Spotify is the most fun and would make the best Medium article. Rating Inflation is the safest bet — the Olist dataset is so rich that we're almost guaranteed to find interesting results.

Open to hearing what everyone thinks — also happy to combine elements if any of these overlap with the other ideas that have been shared.
