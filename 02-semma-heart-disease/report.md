# SEMMA Heart Disease Prediction — Full Project Report

**Course:** CMPE 256 — Data Mining · **Methodology:** SEMMA (Sample, Explore, Modify, Model, Assess)
**Dataset:** UCI Heart Disease, Cleveland processed set — 303 rows × 14 attributes
**Author:** Pranith Varma Pakalapati (San José State University)
**Notebook:** `SEMMA_Heart_Disease.ipynb` (24 cells: 17 code, 7 markdown — executed end-to-end, all cells with outputs)
**Seed:** 42 everywhere. **All numbers below are copied from the executed notebook output — no hand-typed metrics.**

> ⚠️ **CLINICAL DISCLAIMER:** This project is a **teaching demonstration of the SEMMA methodology**. It is **NOT a diagnostic tool** and must never be used to diagnose, triage, or make treatment decisions. The data come from one clinic in the 1980s, the sample is small (303 patients), and the models are classroom baselines. Real clinical use would require regulatory approval, large modern multi-site data, and clinician oversight.

---

## 0. What SEMMA is, and the tooling note

SEMMA — **Sample, Explore, Modify, Model, Assess** — is the data-mining methodology developed for **SAS Enterprise Miner**. It is deliberately model-centric: unlike CRISP-DM, which begins with business understanding and ends with deployment planning, SEMMA assumes the problem is already defined and concentrates on getting from raw data to an assessed model. It has five phases and no separate business-understanding or deployment phase, which is both its strength (focus, speed) and its weakness (see §6, Limitations).

**Tooling note.** SEMMA originated in SAS Enterprise Miner, and the assignment suggests SAS where possible. **No SAS licence was available for this project**, so every SEMMA step is implemented in **Python (scikit-learn, pandas, seaborn)** with its SAS-equivalent node named explicitly. The logic — not the vendor tool — is what is being demonstrated. The mapping is:

| SEMMA phase | SAS Enterprise Miner node(s) | Python equivalent used here |
|---|---|---|
| Sample | Data Partition | `train_test_split` (stratified 80/20, seed 42) + `StratifiedKFold` (5-fold) |
| Explore | StatExplore, Graph Explore, MultiPlot | pandas `describe`/`groupby`, seaborn/matplotlib charts |
| Modify | Impute, Transform Variables, Variable Selection, Replacement | `SimpleImputer`, `OneHotEncoder`, `StandardScaler` in a `ColumnTransformer`/`Pipeline` |
| Model | Regression, Decision Tree, Neural Network, Gradient Boosting | Logistic Regression, Random Forest, HistGradientBoosting |
| Assess | Model Comparison, ROC, Lift, Score | ROC-AUC, confusion matrices, calibration bins, subgroup checks |

One deliberate substitution is flagged in §4: a Neural Network node was **not** used — with n = 303 a neural network would be over-parameterised and unstable, so HistGradientBoosting (the Gradient Boosting node) stands in as the flexible non-linear learner, and this is stated rather than hidden.

---

## 1. Phase 1 — SAMPLE (SAS: Data Partition)

**Sampling strategy.** The full Cleveland set has only **303 rows**. Down-sampling a dataset this small would discard information that cannot be spared, so **no down-sampling was performed** — the whole dataset is used, and the Sample phase is instead a careful, reproducible partition:

- **Stratified 80/20 train/test split** (seed 42): train 242 rows, test 61 rows. Stratification holds the disease rate at 45.9% in both parts (train 0.459, test 0.459).
- **5-fold stratified cross-validation** on the training set for model comparison, so that model choice never rests on a single lucky split.

**Target definition.** The raw `target` is 0 = no disease, 1–4 = disease of increasing severity (counts: 0 → 164, 1 → 55, 2 → 36, 3 → 35, 4 → 13). It is **binarized to 0/1** (0 = no disease, 1 = disease present, i.e. original 1–4). Binarized prevalence is **45.87%** (139 of 303). The severity gradation is discarded deliberately: class 4 has only 13 patients, too few to model, and the binary question is the standard formulation for this dataset.

**Sampling bias and generalizability limits (stated up front, not buried):**

- **Single site, single era:** all patients are from the Cleveland Clinic in the 1980s — one hospital's referral mix, measurement equipment, and practice patterns.
- **Male-heavy:** 206 men vs 97 women (68% male). Disease prevalence is 55.3% in men vs 25.8% in women, so the model mostly learns male presentations of disease.
- **Referral bias:** patients were referred for cardiac evaluation, so they are far sicker than the general population — 45.9% prevalence here vs a low single-digit percentage in the general adult population.
- **Era drift:** diagnostic thresholds (e.g. cholesterol targets) and treatments have changed since the 1980s.

**Consequence:** every result in this report describes *this cohort only*. A model trained here would not be expected to generalise to a modern, multi-site, diverse population without external re-validation.

---

## 2. Phase 2 — EXPLORE (SAS: StatExplore, Graph Explore, MultiPlot)

### 2.1 Shape and missingness

- Shape **(303, 14)**. No duplicated rows; no missing values except the `'?'` codes: **`ca`: 4 missing (1.3%), `thal`: 2 missing (0.7%)** — 6 rows affected in total (2.0%). All other columns: 0 missing.

### 2.2 Univariate distributions (numeric)

| Variable | Mean | Std | Min | Median | Max |
|---|---|---|---|---|---|
| age (years) | 54.44 | 9.04 | 29 | 56 | 77 |
| trestbps (mm Hg) | 131.69 | 17.60 | 94 | 130 | 200 |
| chol (mg/dl) | 246.69 | 51.78 | 126 | 241 | 564 |
| thalach (max HR, bpm) | 149.61 | 22.88 | 71 | 153 | 202 |
| oldpeak (ST depression) | 1.04 | 1.16 | 0 | 0.80 | 6.2 |

Categorical counts: `cp` — 1: 23, 2: 50, 3: 86, 4: 144 (asymptomatic is the largest group); `exang` — no: 204, yes: 99; `thal` — 3 (normal): 166, 6 (fixed defect): 18, 7 (reversible defect): 117; `slope` — 1: 142, 2: 140, 3: 21; `restecg` — 0: 151, 1: 4, 2: 148; `fbs` — 0: 258, 1: 45.

### 2.3 Outliers (IQR rule, 1.5 × IQR)

- `chol`: **5** outliers (bounds 115–371 mg/dl; max 564)
- `trestbps`: **9** outliers (bounds 90–170 mm Hg; max 200)
- `thalach`: **1** outlier; `oldpeak`: **5** outliers; `age`: **0** outliers

Decision (carried into Phase 3): outliers are **kept**. They are physiologically plausible values in cardiac patients, and deleting rows from a 303-row dataset costs more information than it saves.

### 2.4 Correlations with the binarized target

Strongest positive: `exang` **+0.432**, `oldpeak` **+0.425**, `cp` **+0.414**, `slope` +0.339, `sex` +0.277, `age` +0.223. Strongest negative: `thalach` **−0.417**. Notably weak: `chol` **+0.085** and `fbs` +0.025 — cholesterol, a textbook risk factor, barely correlates with disease *in this cohort*. That is a finding, not an error: correlation in one small 1980s referral cohort is not a causal claim, and it warns against dropping variables on univariate correlation alone.

### 2.5 Disease rate by subgroup

- **Sex:** female 25.8% (25/97), male 55.3% (114/206)
- **Chest-pain type (`cp`):** typical angina 30.4%, atypical 18.0%, non-anginal 20.9%, **asymptomatic 72.9%** — the counter-intuitive headline: patients with *no* chest pain were the sickest, because asymptomatic patients in this cohort were referred for other reasons (e.g. abnormal stress tests)
- **Exercise angina (`exang`):** no 30.9%, yes **76.8%**
- **Thal (`thal`):** normal 22.3%, fixed defect 66.7%, reversible defect **76.1%**
- **Slope:** upsloping 25.4%, flat 65.0%, downsloping 57.1%
- **Age group:** 29–45: 25.4% (16/63), 46–55: 37.5% (33/88), 56–65: 62.2% (74/119), 66–77: 48.5% (16/33)

### 2.6 Visualizations (5 charts in the notebook)

1. Target distribution + disease rate by chest-pain type
2. Correlation heatmap (all numeric columns)
3. Age and cholesterol distributions split by disease status
4. ROC curves (all three models, Phase 5)
5. Top-10 Random Forest feature importances (Phase 5)

---

## 3. Phase 3 — MODIFY (SAS: Impute, Transform Variables, Variable Selection)

All steps are implemented inside a scikit-learn `Pipeline`/`ColumnTransformer`, so every fitted quantity (imputation medians, one-hot categories, scaler statistics) is learned from the **training data only** and applied to the test data. The test set is touched exactly once, in Phase 5.

1. **`'?'` → NaN:** `ca` and `thal` converted to numeric with `?` as NaN (after cleaning, the training split still contained 1 missing `ca` and 1 missing `thal`, handled by the imputer).
2. **Median imputation** for `ca` and `thal` (fit on train only). Median, not mean: both are discrete, skewed, low-cardinality columns. With only 6 missing values the choice barely moves results; the procedure is the point.
3. **One-hot encoding** for nominal variables `cp`, `restecg`, `slope` (fit on train only, unknown categories ignored). `thal` is treated as numeric after median imputation (values 3/6/7 behave as an ordinal severity scale in the literature for this dataset; the Random Forest importance check in Phase 5 confirms it carries signal).
4. **Binarize target** (done in Phase 1): 0 vs 1–4.
5. **Scaling** (`StandardScaler`) for the Logistic Regression pipeline only — tree models do not need it, so they get an identical pipeline without the scaler.
6. **Outliers kept** (see §2.3).
7. **Feature selection: no variable dropped.** Rationale — with 13 predictors and 303 rows, dropping a variable on weak univariate correlation (e.g. `chol`, r = +0.09) risks discarding a variable that matters in combination. All 13 are kept; the Phase 5 importance ranking is used to audit this decision after the fact.

**Leakage audit:** no target information, test rows, or whole-dataset statistics leak into training. The re-split after cleaning uses the same seed and stratification, so train/test membership is unchanged in structure.

---

## 4. Phase 4 — MODEL (SAS: Regression, Decision Tree, Neural Network / Gradient Boosting)

Three models spanning the interpretability–flexibility spectrum:

| Model | SAS equivalent | Role |
|---|---|---|
| Logistic Regression (C = 1.0, `max_iter=1000`) | Regression node | Interpretable baseline; coefficients read as log-odds |
| Random Forest (tuned, see below) | Decision Tree node (ensemble) | Non-linearities + interactions; native feature importance |
| HistGradientBoosting (defaults, seed 42) | Gradient Boosting node | Flexible non-linear learner; **stands in for the Neural Network node**, which was deliberately not used — with n = 303 a neural network would be over-parameterised and unstable |

**Tuning.** Light, deliberate tuning for Random Forest only — `GridSearchCV`, 5-fold CV on train, scoring ROC-AUC, grid `n_estimators` ∈ {200, 300} × `max_depth` ∈ {None, 5, 8} × `min_samples_leaf` ∈ {1, 2} (12 combinations). Best parameters: **`max_depth=8, min_samples_leaf=2, n_estimators=200`**, best CV ROC-AUC **0.8918**. The grid is kept small on purpose: with 242 training rows a large grid would overfit the validation folds. Logistic Regression and HistGradientBoosting use defaults.

### 4.1 Results — 5-fold CV (train, n = 242) and held-out test (n = 61)

| Model | CV ROC-AUC (mean ± std) | Test ROC-AUC | Test Accuracy | Test Precision | Test Recall | Test F1 |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.9037 ± 0.0205 | 0.9600 | 0.8525 | 0.7879 | 0.9286 | 0.8525 |
| Random Forest (tuned) | 0.8918 ± 0.0266 | 0.9610 | 0.9180 | 0.8710 | 0.9643 | 0.9153 |
| HistGradientBoosting | 0.8602 ± 0.0214 | 0.9632 | 0.9180 | 0.8710 | 0.9643 | 0.9153 |

Two honest observations:

- **The ranking flips between CV and test.** By cross-validation (the more stable estimate — 5 folds × 242 rows), Logistic Regression is best (0.9037); by the 61-row test set, HistGradientBoosting is best (0.9632). With a test set of 61, a single patient is worth ~0.016 of AUC, so a 0.002–0.003 gap between models is noise, not a real difference. No honest report can crown a winner on test AUC alone here.
- **Random Forest and HistGradientBoosting make identical test errors** (see confusion matrices below) — same accuracy, precision, recall, and F1.

---

## 5. Phase 5 — ASSESS (SAS: Model Comparison, ROC, Lift, Score)

### 5.1 Confusion matrices (test set, n = 61; [[TN, FP], [FN, TP]])

- **Logistic Regression:** [[26, 7], [2, 26]] — 2 missed cases (false negatives), 7 false alarms
- **Random Forest:** [[29, 4], [1, 27]] — 1 missed case, 4 false alarms
- **HistGradientBoosting:** [[29, 4], [1, 27]] — identical to Random Forest

In a clinical framing, a false negative (missed disease) is far costlier than a false positive, so **recall on the disease class matters more than raw accuracy**. Random Forest / HistGradientBoosting recall is 0.9643 (27/28 cases found) vs 0.9286 for Logistic Regression (26/28) — a difference of exactly one patient.

### 5.2 ROC curves

All three curves sit well above chance (AUC 0.960–0.963 on test; chance = 0.500). The curves are close together and cross, consistent with the "statistical tie" reading above. (Figure: `figures/fig_roc_curves.png`.)

### 5.3 Calibration (best model by test AUC — HistGradientBoosting; test set)

| Predicted-probability bin | n | Mean predicted | Observed disease rate |
|---|---|---|---|
| (0.0, 0.2] | 25 | 0.053 | 0.00 |
| (0.2, 0.4] | 5 | 0.309 | 0.20 |
| (0.4, 0.6] | 2 | 0.530 | 0.50 |
| (0.6, 0.8] | 4 | 0.663 | 0.75 |
| (0.8, 1.0] | 25 | 0.976 | 0.92 |

Calibration is broadly sensible (low predicted → low observed, high → high) and the middle bins track well, but the middle bins contain only 2–5 patients each — this is indicative, not proven. No recalibration (e.g. Platt/isotonic) was applied: with 61 test rows there is not enough data to fit one honestly.

### 5.4 Feature importance (Random Forest, top 10)

`thal` 0.150, `ca` 0.125, `cp_4.0` (asymptomatic) 0.107, `thalach` 0.097, `oldpeak` 0.085, `age` 0.067, `chol` 0.064, `trestbps` 0.062, `exang` 0.058, `slope_1.0` 0.038. The importance ranking corroborates Phase 2 (thal, ca, cp, thalach, oldpeak dominate) and justifies keeping `chol` — it contributes (0.064) even though its univariate correlation was only +0.085.

Logistic Regression coefficients agree in direction: largest positive — `ca` +1.129, `cp_4.0` +0.951, `sex` +0.698, `thal` +0.658, `slope_2.0` +0.591; largest negative — `cp_1.0` −0.666, `slope_1.0` −0.471, `cp_3.0` −0.469, `thalach` −0.352. A positive coefficient raises the log-odds of disease.

### 5.5 Fairness / subgroup check (best model, test set — small n, wide uncertainty)

- Female: n = 20, recall 1.00, AUC 1.00 · Male: n = 41, recall 0.95, AUC 0.95
- Age 29–45: n = 16, recall 1.00, AUC 1.00 · 46–55: n = 15, recall 1.00, AUC 1.00 · 56–65: n = 24, recall 0.94, AUC 0.90 · 66–77: n = 6, recall 1.00, AUC 0.78

No subgroup looks disadvantaged beyond noise, but **these numbers cannot prove fairness**: the smallest group has 6 patients, and the training data are 68% male and single-site. A deployment-grade fairness audit would need a larger, representative cohort. This check is reported because SEMMA's Assess phase demands it, not because it settles the question.

### 5.6 Deployment recommendation

**Recommended model: Random Forest (tuned)** — as a **research/teaching prototype only**, not as a clinical device.

Why Random Forest, given the statistical tie: (1) joint-best test accuracy (0.9180), precision (0.8710), recall (0.9643), and F1 (0.9153); (2) test AUC 0.9610, within 0.002 of HistGradientBoosting — indistinguishable on 61 patients; (3) unlike HistGradientBoosting it yields direct, explainable feature importances; (4) unlike Logistic Regression it captures non-linearities without giving up stability (CV AUC 0.8918 ± 0.0266). **HistGradientBoosting is the designated challenger** — if it wins again on a larger validation set, it replaces the champion. Logistic Regression remains the interpretable fallback and the CV leader (0.9037), and would be the choice if regulators required coefficient-level explainability.

**What "deployment" means here:** a prototype that outputs a risk score for retrospective research use, with a human clinician in the loop, no automated decisions, and the following monitoring plan:

- **Re-validate** on a different hospital and a modern cohort before any pilot; expect performance to drop.
- **Track input drift** (compare incoming age/sex/chol distributions with the 1980s Cleveland training distribution) and **re-check calibration quarterly**.
- **Log subgroup recall/AUC** by sex and age band; halt use if any subgroup's recall falls materially below the overall figure.
- **Re-train** on modern, multi-site, consented data; retire this model once that exists.

### 5.7 Ethics

The data are de-identified and public (UCI); no new patient data were collected and no person is identifiable. The fairness check (§5.5) is limited by small subgroup sizes and must not be read as proof of fairness. The clinical disclaimer at the top of this report applies to every number in it.

---

## 6. Limitations (what SEMMA itself does not cover)

1. **No business-understanding phase.** SEMMA starts after the problem is defined; the clinical framing, cost of errors, and deployment context in this report were supplied by the analyst, not by the methodology.
2. **No deployment phase.** SEMMA ends at Assess; the monitoring plan in §5.6 is an analyst add-on, borrowed from CRISP-DM thinking.
3. **Small, old, single-site data** (see §1) — the dominant limitation of the whole project.
4. **Test set of 61** — model ranking is unstable; all "best model" claims are within noise.
5. **No neural network** was trained (substitution documented in §4); no hyperparameter search beyond the small Random Forest grid; no recalibration.
6. **Binary target discards severity** (classes 1–4 collapsed); a severity model would need far more data.

---

## 7. Reproducibility

- Notebook: `SEMMA_Heart_Disease.ipynb` — Colab-ready (cell 1 installs dependencies with `%pip`; cell 2 downloads the data from UCI). All 17 code cells executed with outputs; 5 charts embedded.
- Data: `data/processed.cleveland.data` + `data/DATA_DICTIONARY.md`
- Results table: `model_comparison.csv` (generated by the notebook)
- Figures: `figures/` (5 PNGs, also embedded in the notebook)
- Environment: `requirements.txt`; seed 42 everywhere; no hard-coded local paths.

## 8. Artifacts delivered

| Artifact | File |
|---|---|
| Executed notebook (Colab-ready) | `SEMMA_Heart_Disease.ipynb` |
| Raw data + dictionary | `data/processed.cleveland.data`, `data/DATA_DICTIONARY.md` |
| This report | `report.md` |
| Medium article draft | `medium-article.md` |
| Critic revision log | `critic-revisions.md` |
| Video walkthrough script | `video-script.md` |
| Setup / run guide | `README.md`, `requirements.txt` |
| Model comparison table | `model_comparison.csv` |
