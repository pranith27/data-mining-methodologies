# Data Dictionary — UCI Wine Quality (Red Wine)

**Source:** Cortez, Cerdeira, Almeida & Reis (2009), "Modeling wine preferences by data mining from physicochemical properties", *Decision Support Systems* 47(4). UCI Machine Learning Repository: https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv

**File:** `winequality-red.csv` — semicolon-separated (`;`), header row present, 1,599 rows × 12 columns. Downloaded from the UCI URL above; no modifications to the file.

**Scope:** Red wines of the Vinho Verde region, Portugal. Each row is one wine sample. The white-wine file from the same source (4,898 rows) is intentionally **not** included — red and white wines have different chemistry baselines and are modelled separately.

## Attributes

| # | Column | Type | Unit / scale | Description |
|---|---|---|---|---|
| 1 | fixed acidity | float | g/L (tartaric acid) | Non-volatile acids (mainly tartaric, malic, citric, succinic) that stay in the wine |
| 2 | volatile acidity | float | g/L (acetic acid) | Volatile acids, chiefly acetic acid; high values give a vinegar fault |
| 3 | citric acid | float | g/L | Adds freshness and flavour; small amounts are normal in red wine |
| 4 | residual sugar | float | g/L | Sugar remaining after fermentation |
| 5 | chlorides | float | g/L (sodium chloride) | Salt content; high values taste salty |
| 6 | free sulfur dioxide | float | mg/L | SO₂ not bound to other compounds; the active antimicrobial/antioxidant fraction |
| 7 | total sulfur dioxide | float | mg/L | Free + bound SO₂; the total amount dosed |
| 8 | density | float | g/mL | Density of the wine; close to water (0.99–1.00), higher with more sugar |
| 9 | pH | float | 0–14 scale | Acidity level; lower pH = more acidic; typical red wine 3.0–3.8 |
| 10 | sulphates | float | g/L (potassium sulphate) | Contributes to aroma and body; a wine additive |
| 11 | alcohol | float | % by volume | Ethanol content |
| 12 | quality | integer | 0–10 (observed 3–8) | **Target.** Median sensory score from at least 3 trained tasters |

## Target distribution (as downloaded, before preprocessing)

| quality | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|
| count | 10 | 53 | 681 | 638 | 199 | 18 |

Mean quality 5.64, standard deviation 0.81. Scores 5 and 6 hold 82.5% of the wines. High quality (≥ 7): 217 wines, 13.57%.

## Data quality (verified by code in the notebook)

- **Missing values:** 0 in every column — no imputation needed.
- **Exact duplicate rows:** 240 (15.0%). Dropped in preprocessing (Step 2) → 1,359 unique wines, because identical rows can leak across the train/test split.
- **Skew:** strongly right-skewed — chlorides 5.68, residual sugar 4.54, sulphates 2.43, total sulfur dioxide 1.52, free sulfur dioxide 1.25. Handled with log1p in transformation (Step 3).
- **Outliers (IQR rule):** residual sugar 155, chlorides 112, sulphates 59, total SO₂ 55, fixed acidity 49, density 45, pH 35, free SO₂ 30, volatile acidity 19, alcohol 13, citric acid 1. Kept, not deleted: these are real wines, not measurement errors.

## Engineered features (created in the notebook, Step 3)

| Feature | Definition | Rationale |
|---|---|---|
| total_acidity | fixed acidity + volatile acidity + citric acid | Total acid load as experienced by the taster |
| sulphur_ratio | free sulfur dioxide / total sulfur dioxide | Share of dosed sulphur that is actually active/protective |
| alcohol_x_va | alcohol × volatile acidity | Interaction: alcohol may mask or compound volatile-acidity faults |

## Derived targets (created in the notebook)

| Target | Definition |
|---|---|
| quality (regression) | The raw sensory score, 3–8 |
| high_quality (classification) | 1 if quality ≥ 7, else 0 — "premium" vs the rest (13.54% positive after dedup) |

## What is NOT in this data

Grape variety, vintage year, vineyard/region beyond Vinho Verde, price, tannin measurements, and taster identity are all absent. Any of these could influence quality; their absence caps the achievable accuracy and is stated as a limitation in the report.
