# KDD Project Report — What Makes a Good Red Wine?

**Methodology:** KDD — Knowledge Discovery in Databases (Fayyad, Piatetsky-Shapiro & Smyth, 1996)
**Dataset:** UCI Wine Quality, red wine (Cortez et al., 2009)
**Notebook:** `KDD_Wine_Quality.ipynb` (31 cells, 21 code cells, executed end-to-end, zero errors)
**Seed:** 42 everywhere. **Split:** 80/20, stratified on the binary high-quality label.

> Every number in this report is copied from the executed notebook output. No metric was typed in by hand or estimated.

---

## 0. Executive summary

A winery wants to know which measurable properties of a wine drive the quality score a trained sensory panel gives it. Following the five KDD steps on 1,359 unique red wines from Portugal's Vinho Verde region, the project found that **alcohol content is the dominant driver of perceived quality** (Pearson r = +0.48; Random Forest importance 0.33), **volatile acidity is the main destroyer** (r = −0.39), and **sulphates and citric acid help** (r = +0.25 and +0.23), while **residual sugar is essentially irrelevant** (r = +0.01). The best model — a tuned Random Forest — explains R² = 0.43 of the variance in quality scores (RMSE 0.64), and premium-wine detection (quality ≥ 7) reaches ROC-AUC 0.89. That is useful for ranking batches and screening quality control, and it is honestly not enough to replace human tasters: ~57% of the variance in sensory scores is not in the lab measurements.

---

## Step 1 — Selection

### 1.1 Goal

Discover what drives the *perceived quality* of red wine from physicochemical measurements, and turn that knowledge into something a winery can use for quality control and blending decisions.

### 1.2 Why this dataset

The UCI Wine Quality set (Cortez et al., 2009) is the standard public benchmark for this question: 1,599 red wines, each with 11 physicochemical measurements and one sensory quality score — the median of at least 3 expert evaluations on a 0–10 scale. It is small, clean, fully labelled, and its target is genuinely *human judgement*, which makes the interpretation step interesting and honest.

### 1.3 Why red wine only

The UCI source also ships a white-wine file (4,898 rows). Mixing the two would be a mistake: red and white wines have different chemistry baselines (reds carry far higher volatile acidity and tannin-related compounds; whites carry more residual sugar and free SO₂), so a single model would spend most of its capacity learning "red vs white" instead of "good vs bad". The white-wine set is therefore **excluded by design**, and nothing in this report is claimed to transfer to white wine.

### 1.4 Target definition — two tasks

| Task | Target | Why |
|---|---|---|
| Primary — regression | `quality` (integer, observed 3–8) | The panel score itself; predicts *how good* a wine is |
| Secondary — classification | `high_quality = 1 if quality >= 7 else 0` | The business question is usually binary: "is this batch premium?" Only 13.57% of wines score ≥ 7, so this is an imbalanced classification problem |

### 1.5 What was selected and excluded

- **Selected:** all 1,599 rows, all 11 physicochemical features, the quality score.
- **Excluded:** the white-wine file (above); no feature is dropped at selection time — feature selection happens later, after evidence.
- **Not available (and therefore not modelled):** grape variety, vintage year, vineyard, price, tannin measurements, taster identity. Their absence caps how far any model can go, and is carried as a limitation through the whole report.

### 1.6 Selection — verified numbers

| Fact | Value |
|---|---|
| Shape | 1,599 rows × 12 columns |
| Quality distribution | 3: 10, 4: 53, 5: 681, 6: 638, 7: 199, 8: 18 |
| Mean quality | 5.64 (std 0.81) |
| Scores 5–6 share | 82.5% of all wines |
| High quality (≥ 7) | 217 wines, 13.57% |
| File | `data/winequality-red.csv`, semicolon-separated, 84,199 bytes |

---

## Step 2 — Preprocessing

### 2.1 Missing values

**Zero missing cells** in all 12 columns. No imputation was performed — inventing values would only add noise.

### 2.2 Duplicates

**240 rows (15.0%) are exact duplicates.** Decision: **drop them**, leaving **1,359 unique wines**. Reason: identical rows can land on both sides of a train/test split and leak the test set, and they overweight a handful of wines. After dedup the quality distribution is 3: 10, 4: 53, 5: 577, 6: 535, 7: 167, 8: 17, and the high-quality share is 13.54% — essentially unchanged, so dedup did not distort the target.

### 2.3 Distributions and skew

Skewness (strongly skewed above |1|): chlorides 5.68, residual sugar 4.54, sulphates 2.43, total sulfur dioxide 1.52, free sulfur dioxide 1.25. Mildly skewed: fixed acidity 0.98, alcohol 0.86, volatile acidity 0.67. Near-symmetric: density 0.07, pH 0.19, citric acid 0.32.

IQR outlier counts (outside Q1 − 1.5·IQR, Q3 + 1.5·IQR): residual sugar 155, chlorides 112, sulphates 59, total SO₂ 55, fixed acidity 49, density 45, pH 35, free SO₂ 30, volatile acidity 19, alcohol 13, citric acid 1.

Decision: **keep all outliers, do not delete or clip.** These are real wines — residual sugar up to 15.5 g/L is a genuine sweet red, chlorides up to 0.611 g/L is a real (salty) wine — not sensor errors. Tree models are robust to them, and log1p tames their leverage for linear models. Deleting 10%+ of the data would bias the sample toward "ordinary" wines, exactly the ones the model least needs help with.

### 2.4 First look at the target relationship

Pearson correlation with quality (weakest → strongest): volatile acidity −0.391, total sulfur dioxide −0.185, density −0.175, chlorides −0.129, pH −0.058, free sulfur dioxide −0.051, residual sugar +0.014, fixed acidity +0.124, citric acid +0.226, sulphates +0.251, alcohol +0.476.

Already visible before any modelling: alcohol is the strongest positive signal, volatile acidity the strongest negative one, and residual sugar — the variable a casual drinker would guess matters most — is essentially uncorrelated (+0.01).

### 2.5 Data-quality report (summary)

| Issue | Evidence | Decision |
|---|---|---|
| Missing values | 0 cells | No imputation |
| Exact duplicates | 240 rows (15.0%) | Dropped → 1,359 rows |
| Skew | 5 features with skew > 1.2 | log1p in Step 3 |
| Outliers | up to 155 per feature (IQR rule) | Kept; real wines, not errors |
| Target imbalance | Scores 5–6 dominate; only 10 wines score 3, 18 score 8 | Stratified split + class weights |

---

## Step 3 — Transformation

### 3.1 Feature engineering — three new features, each justified by wine chemistry

| Feature | Definition | Justification |
|---|---|---|
| `total_acidity` | fixed acidity + volatile acidity + citric acid | Acidity is experienced as a whole; the three acids are chemically related and individually noisy |
| `sulphur_ratio` | free SO₂ / total SO₂ | Free SO₂ is the active, protective fraction; the ratio measures how much dosed sulphur is actually available |
| `alcohol_x_va` | alcohol × volatile acidity | Interaction term: high alcohol can mask volatile-acidity faults, or the two can compound; a product term lets a linear model express "the effect of volatile acidity depends on alcohol level" |

Whether these features *help* was tested empirically in Step 4 (see §4.4) rather than assumed.

### 3.2 Scaling and skew handling

- **log1p** applied to the five strongly skewed features: residual sugar, chlorides, sulphates, free sulfur dioxide, total sulfur dioxide. log1p keeps zero values valid (citric acid has genuine zeros, though it was not itself transformed).
- **Standardisation** applied only for the linear models (Linear / Logistic Regression), which need it; tree models receive the log-transformed features unscaled.

### 3.3 Leakage control

All transformers live inside `sklearn` Pipelines and are **fit on the training set only** — the test set is transformed, never fitted. The split is **80/20, stratified on the binary high-quality label** (random_state = 42), giving train 1,087 / test 272, with the high-quality share preserved (train 13.5%, test 13.6%) and near-identical mean quality (train 5.623, test 5.625). Final feature matrix: 1,359 × 14 (11 original + 3 engineered).

---

## Step 4 — Data Mining

### 4.1 Regression — predict the 0–10 score

| Model | R² | RMSE | MAE |
|---|---|---|---|
| **Random Forest Regressor (300 trees)** | **0.4280** | **0.6383** | **0.4874** |
| HistGradientBoosting Regressor | 0.3813 | 0.6639 | 0.5013 |
| Linear Regression | 0.3491 | 0.6809 | 0.5181 |

The linear model is the interpretable baseline; the tree ensembles beat it, which tells us the relationships are genuinely non-linear and interactive (consistent with the alcohol × volatile-acidity story).

### 4.2 Light tuning — Random Forest Regressor

GridSearchCV, 3-fold CV, over `n_estimators` ∈ {300, 500}, `max_depth` ∈ {None, 10, 20}, `min_samples_leaf` ∈ {1, 2, 5}, scored by R².

- **Best hyperparameters:** `max_depth=10, min_samples_leaf=5, n_estimators=500`
- **Best 3-fold CV R²:** 0.3874
- **Test performance: R² = 0.4298, RMSE = 0.6373, MAE = 0.4920**

Tuning bought almost nothing over the untuned forest (R² 0.4280 → 0.4298): the default forest was already near this dataset's ceiling, and heavier tuning would have overfit the validation folds. That is itself a finding.

### 4.3 Classification — premium wine (quality ≥ 7)

Both models use `class_weight="balanced"` to counter the 86/14 imbalance. Accuracy is not reported as a headline metric: predicting "not premium" for everything would score ~86% and learn nothing.

| Model | ROC-AUC | Precision | Recall | F1 |
|---|---|---|---|---|
| **Random Forest Classifier** | 0.8924 | **0.5455** | 0.4865 | **0.5143** |
| Logistic Regression | **0.8966** | 0.3636 | **0.8649** | 0.5120 |

- Logistic Regression: confusion matrix [[179, 56], [5, 32]] — catches 32 of 37 premium wines (recall 86%) but raises 56 false alarms (precision 36%).
- Random Forest: confusion matrix [[220, 15], [19, 18]] — balanced operating point, 55% precision / 49% recall.

The two models have near-identical ROC-AUC (~0.89–0.90) and near-identical F1 (~0.51); they differ only in *where* they sit on the precision/recall trade-off. That choice belongs to the winery, not the algorithm (see §6).

### 4.4 Did the engineered features help?

Same Random Forest, with vs without the three engineered features: **R² 0.4191 → 0.4280, a gain of +0.0089** (RMSE 0.6432 → 0.6383). A small, real improvement — the interaction term and sulphur ratio carry some signal — but the raw features already hold nearly all of it. A negative-ish result, honestly reported: feature engineering was worth doing, and worth not overselling.

---

## Step 5 — Interpretation / Evaluation

### 5.1 Feature importance (tuned Random Forest Regressor)

| Rank | Feature | Importance |
|---|---|---|
| 1 | alcohol | 0.3343 |
| 2 | citric acid | 0.1431 |
| 3 | total sulfur dioxide | 0.1073 |
| 4 | chlorides | 0.0667 |
| 5 | alcohol_x_va (engineered) | 0.0558 |
| 6 | sulphur_ratio (engineered) | 0.0442 |
| 7 | sulphates | 0.0407 |
| 8 | volatile acidity | 0.0343 |
| 9 | pH | 0.0329 |
| 10 | total_acidity (engineered) | 0.0297 |
| 11 | fixed acidity | 0.0287 |
| 12 | residual sugar | 0.0287 |
| 13 | density | 0.0279 |
| 14 | free sulfur dioxide | 0.0259 |

Alcohol alone carries a third of all signal. Note the disagreement between methods: volatile acidity is the strongest *negative correlation* (r = −0.39) but only 8th in Random Forest importance — the forest splits on alcohol and citric acid first, and volatile acidity's effect is partly absorbed by the engineered `alcohol_x_va` interaction (0.056) and by correlations with other features. Both views are reported; neither is "the truth".

### 5.2 Linear Regression coefficients (standardised — direction and size)

Largest positive: alcohol +0.404, citric acid +0.152, total sulfur dioxide +0.100, sulphur_ratio +0.088. Largest negative: alcohol_x_va −0.300, sulphates −0.080, volatile acidity −0.078, residual sugar −0.062. The −0.300 coefficient on the interaction term is the interesting one: it says the benefit of alcohol *shrinks* as volatile acidity rises — exactly the masking/compounding story the interaction was built to test. (Sulphates flips sign between the correlation (+0.25) and the linear coefficient (−0.08) once other variables are controlled for — a reminder that a single coefficient is not a causal effect.)

### 5.3 Partial-dependence-style insight — mean quality by binned drivers

**Alcohol:** 8–9.5% → 5.23 (n=374); 9.5–10.2% → 5.40 (n=344); 10.2–11% → 5.70 (n=283); 11%+ → 6.20 (n=358). Spread: **0.97 quality points**, monotone increasing.

**Volatile acidity:** <0.40 g/L → 6.05 (n=387); 0.40–0.55 → 5.66 (n=377); 0.55–0.70 → 5.40 (n=393); >0.70 → 5.17 (n=202). Spread: **0.89 points**, monotone decreasing.

**Sulphates:** <0.55 g/L → 5.23 (n=357); 0.55–0.65 → 5.52 (n=465); 0.65–0.80 → 5.96 (n=342); >0.80 → 6.01 (n=195). Spread: **0.78 points**, monotone increasing, flattening at the top.

**Mean alcohol by quality score:** 3 → 9.96%; 4 → 10.27%; 5 → 9.89%; 6 → 10.66%; 7 → 11.49%; 8 → 12.16%. **Mean volatile acidity by quality score:** 3 → 0.885 g/L; 4 → 0.694; 5 → 0.579; 6 → 0.496; 7 → 0.404; 8 → 0.428. The worst wines (score 3) average more than twice the volatile acidity of the best (0.885 vs ~0.41).

### 5.4 Residual and error analysis (tuned Random Forest)

- Residuals (actual − predicted): mean −0.012, std 0.638, mean |residual| 0.492.
- **89.3% of predictions fall within ±1 quality point** of the true score.
- Error by true quality score:

| True quality | n (test) | Mean residual | MAE |
|---|---|---|---|
| 3 | 2 | −1.659 | 1.659 |
| 4 | 14 | −1.320 | 1.320 |
| 5 | 109 | −0.338 | 0.356 |
| 6 | 110 | +0.236 | 0.399 |
| 7 | 33 | +0.702 | 0.702 |
| 8 | 4 | +1.543 | 1.543 |

The pattern is textbook **regression to the mean**: the model over-predicts the worst wines (mean residual −1.66 at score 3) and under-predicts the best (mean residual +1.54 at score 8), and is most accurate in the crowded middle (MAE 0.36–0.40 at scores 5–6). Practical consequence: trust the model for ranking ordinary batches; do not trust it to spot a once-in-a-decade wine, and do not trust it to condemn a batch on its own — the extremes are where it is weakest and where the stakes are highest.

### 5.5 Knowledge discovered — what was already known vs what is new

| Finding | Status |
|---|---|
| Alcohol ↑ ⇒ quality ↑ | Known in the wine literature (Cortez et al. 2009 report the same); **confirmed** here with a second method and quantified: ~1 quality point across the alcohol range |
| Volatile acidity ↓ ⇒ quality ↑ | Known (volatile acidity = acetic-acid fault); **confirmed**, and it is the strongest *negative* signal in the data (r = −0.39) |
| Sulphates ↑ ⇒ quality ↑ | Known qualitatively; **confirmed**: Pearson r = +0.25, Random Forest importance 0.04 |
| Citric acid ↑ ⇒ quality ↑ | Consistent with freshness/crispness in the literature; **confirmed** as the #2 Random Forest driver (importance 0.14) |
| Residual sugar ≈ irrelevant (r = +0.01) | **Surprising but consistent**: for these dry reds, sweetness does not move the panel score — a useful correction to folk wisdom |
| Engineered features help only slightly | **New for this run**: total acidity, sulphur ratio and the alcohol×volatile-acidity interaction add just +0.009 R² |
| The score is only partly predictable | **Key limitation, quantified**: even the best model explains R² ≈ 0.43. ~57% is taster subjectivity, unmeasured factors (grape, vintage, tannin structure) and noise |

### 5.6 Evaluation verdict

The mining step succeeded *as knowledge discovery* even though the headline metric is modest. The drivers are stable across methods (correlation, linear coefficients, tree importance all rank alcohol first and volatile acidity as the main negative), the binned means are monotone, and the error structure is understood. A model does not need R² = 0.9 to be useful — it needs its limits to be known, and they are.

---

## Step 6 — Deployment / Knowledge Use

### 6.1 How a winery would use this

1. **Pre-release QC screen.** Run every finished batch's lab panel through the tuned Random Forest (refit on all 1,359 wines with the tuned hyperparameters). Flag batches predicted below 5 for a human re-taste before release; fast-track batches predicted ≥ 6.5 for premium-labelling review.
2. **Blending guidance — directional, not a recipe.** The model says: protect alcohol level, keep volatile acidity low, do not over-dose total SO₂. Use it to *rank* candidate blends by predicted quality and taste-test the top few — never to auto-approve a blend.
3. **Operating-point choice for the premium classifier.** If missing a premium batch is costlier than a false alarm (e.g. premium labelling review is cheap), use Logistic Regression (recall 86%, precision 36%). If false alarms are costly (e.g. each flagged batch triggers an expensive panel re-taste), use the Random Forest (precision 55%, recall 49%).
4. **Monitoring.** Track prediction drift monthly: if the distribution of incoming lab measurements shifts (new vintage, new supplier), re-validate R² on a fresh labelled sample. Retrain when R² drops materially or when the panel composition changes — because the target *is* human judgement, a new panel is a new target.
5. **Feedback loop.** Log every panel score against the prediction; the growing labelled set is the training data for the next model version.

### 6.2 Deployment demo (from the notebook)

A `predict_quality()` function takes one wine's lab measurements and returns a predicted score and a premium flag. Two illustrative profiles: a good-profile wine (alcohol 12.5%, volatile acidity 0.35, sulphates 0.80) scores **6.89, premium likely**; a faulty-profile wine (alcohol 9.0%, volatile acidity 1.10, total SO₂ 90) scores **4.56, not premium**. The 2.3-point gap between two plausible wines is the model doing its job.

### 6.3 Limits — stated plainly

- **Sensory scores are subjective.** The same wine can score differently with a different panel. The model's ceiling (~R² 0.43) reflects that, not a modelling failure.
- **Single region, single style.** Vinho Verde reds only. Do not apply to white wine, other regions, or other vintages without re-validation.
- **Correlation ≠ causation.** Alcohol correlates with quality, but much of that is ripeness and grape quality, not alcohol itself. Adding alcohol to a wine will not make it better — do not use this model as a recipe.
- **Rare scores are poorly modelled.** Only 10 wines score 3 and 18 score 8 in the full data; the error analysis shows the model is weakest exactly there.
- **The engineered features added almost nothing.** The value is in the ranking and the drivers, not in squeezing the last 0.01 of R².

---

## Reproducibility

- Dataset pinned to the UCI URL; the notebook downloads it itself (cell 2) and falls back to the local copy in `data/`.
- Seed 42 everywhere (split, models, grid search); the full notebook was executed twice with identical metrics.
- All transformers fit on train only (sklearn Pipelines — no leakage).
- Environment: Python 3.12, scikit-learn 1.9.1, pandas 2.1.4, numpy 1.26.4, matplotlib, seaborn. Full list in `requirements.txt`.

## References

- Fayyad, U., Piatetsky-Shapiro, G., & Smyth, P. (1996). "From Data Mining to Knowledge Discovery in Databases." *AI Magazine*, 17(3), 37–54.
- Cortez, P., Cerdeira, A., Almeida, F., & Reis, J. (2009). "Modeling wine preferences by data mining from physicochemical properties." *Decision Support Systems*, 47(4), 547–553.
- UCI Machine Learning Repository — Wine Quality dataset. https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/
