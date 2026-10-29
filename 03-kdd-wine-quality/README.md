# KDD — What Makes a Good Red Wine?

A complete, end-to-end **KDD (Knowledge Discovery in Databases)** project on the UCI Wine Quality dataset — every step of the Fayyad et al. (1996) process, from selection to deployment, with real executed results.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pranith27/data-mining-methodologies/blob/main/03-kdd-wine-quality/KDD_Wine_Quality.ipynb)

## The question

Which measurable properties of a red wine drive the quality score a trained sensory panel gives it — and can a winery use that knowledge?

## Dataset

UCI Wine Quality — red wine (Cortez et al., 2009): **1,599 wines, 11 physicochemical features + 1 sensory quality score** (0–10 scale, observed 3–8), from the Vinho Verde region of Portugal. After dropping 240 exact duplicate rows: **1,359 unique wines**.

## What the project found

- **Alcohol is the dominant driver** of perceived quality (Pearson r = +0.48; Random Forest importance 0.33). Wines above 11% alcohol average 6.20; wines at 8–9.5% average 5.23 — nearly a full quality point.
- **Volatile acidity is the main quality killer** (r = −0.39): wines below 0.40 g/L average 6.05, above 0.70 g/L average 5.17.
- **Sulphates and citric acid help** (r = +0.25 and +0.23). **Residual sugar is irrelevant** (r = +0.01) — a useful correction to folk wisdom about sweet reds.
- Best regression model (tuned Random Forest): **R² = 0.43, RMSE = 0.64** — good for ranking and QC screening, not for replacing tasters.
- Premium-wine detection (quality ≥ 7): **ROC-AUC = 0.89–0.90**, best F1 = 0.51.
- Feature engineering (total acidity, sulphur ratio, alcohol × volatile acidity) added only **+0.009 R²** — a genuine negative result.
- Honest ceiling: ~57% of the variance in sensory scores is not in the lab measurements (taster subjectivity, grape, vintage, tannins — all unmeasured here).

## Contents

| File | What it is |
|---|---|
| `KDD_Wine_Quality.ipynb` | The full project — all 5 KDD steps + deployment, executed top-to-bottom |
| `data/winequality-red.csv` | The dataset (UCI, semicolon-separated) |
| `data/DATA_DICTIONARY.md` | Every attribute, target distribution, data-quality audit |
| `report.md` | Detailed step-by-step KDD report with all real numbers |
| `medium-article.md` | Medium-ready article draft (~1,500 words) |
| `critic-revisions.md` | Critic log — 3 revision rounds against a world-renowned-KDD-authority persona |
| `video-script.md` | 6-minute YouTube walkthrough script with timestamps |
| `requirements.txt` | Python dependencies |

## Run it

### Option A — Google Colab (recommended)

Click the badge above, or upload `KDD_Wine_Quality.ipynb` to Colab. The first code cell installs dependencies and the second downloads the dataset from UCI — nothing else to set up. Runtime → Run all.

### Option B — Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook KDD_Wine_Quality.ipynb
```

Or execute it headlessly to verify:

```bash
jupyter nbconvert --to notebook --execute --inplace KDD_Wine_Quality.ipynb
```

## Reproduce it

- **Seed 42 everywhere** (split, models, grid search).
- All transformers are fit on the training set only (pipelines — no leakage).
- Split: 80/20, stratified on the binary high-quality label.
- The notebook was executed end-to-end and every cell produced output; see `report.md` for the exact numbers the executed notebook produced.

## KDD steps covered

1. **Selection** — goal, why red wine only, dual target (regression + binary premium classification)
2. **Preprocessing** — missing/duplicates/outliers/skew audit with handling decisions
3. **Transformation** — log1p, scaling, 3 engineered features (tested, not assumed), leakage-free split
4. **Data Mining** — Linear Regression, Random Forest, HistGradientBoosting; Logistic Regression + Random Forest classifier; light GridSearchCV tuning
5. **Interpretation / Evaluation** — feature importance, coefficients, binned drivers, residual + error-by-score analysis, known-vs-new knowledge
6. **Deployment / Knowledge Use** — winery QC screen, blending guidance, monitoring plan, stated limits

## Limits (stated plainly)

Sensory scores are subjective; single region and style (Vinho Verde reds); correlation is not causation — alcohol correlates with quality, but adding alcohol to a wine will not make it better. Do not use this model as a recipe.

## References

- Fayyad, Piatetsky-Shapiro & Smyth (1996). "From Data Mining to Knowledge Discovery in Databases." *AI Magazine* 17(3).
- Cortez, Cerdeira, Almeida & Reis (2009). "Modeling wine preferences by data mining from physicochemical properties." *Decision Support Systems* 47(4).
- UCI Machine Learning Repository: Wine Quality dataset.
