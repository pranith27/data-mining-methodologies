# Video Script — SEMMA Heart Disease Prediction (6-minute walkthrough)

**Format:** YouTube walkthrough of the notebook and results. Total runtime 6:00. Speak at a natural pace; on-screen cues are marked **[ON SCREEN]**.

---

## 0:00–0:30 — Hook

**[ON SCREEN: title card — "SEMMA in 6 Minutes: Predicting Heart Disease on 303 Patients"]**

"In this video I run a complete SEMMA project — Sample, Explore, Modify, Model, Assess — on the UCI Heart Disease dataset. And the headline result is not what you'd expect: the two best models tied, and the sickest patients were the ones with no chest pain at all. Before anything else: this is a teaching demo, not a diagnostic tool. Nobody's heart should ever be judged by a 303-row dataset from the 1980s."

## 0:30–1:10 — What SEMMA is (40s)

**[ON SCREEN: SEMMA diagram — five boxes S → E → M → M → A; small text: "SAS Enterprise Miner methodology"]**

"SEMMA is the methodology built for SAS Enterprise Miner. Five phases. Unlike CRISP-DM, it skips business understanding and deployment — it assumes the problem is defined and focuses on getting to an assessed model. I had no SAS licence for this project, so every phase is implemented in Python with scikit-learn, and every phase names its SAS-equivalent node — Data Partition, StatExplore, Impute, Regression, Model Comparison. The logic is what matters, not the vendor."

## 1:10–2:00 — Sample + Explore (50s)

**[ON SCREEN: notebook — Phase 1 Sample cell output: shape (303, 14), prevalence 0.4587]**

"Sample: 303 rows, so no down-sampling — instead a stratified 80/20 split, 242 train, 61 test, seed 42, plus 5-fold cross-validation. And the caveats up front: single hospital, 1980s, 68% male, referral population with 45.9% disease prevalence. These results describe that cohort only."

**[ON SCREEN: chart — disease rate by chest-pain type; asymptomatic bar at 72.9% highlighted]**

"Explore: only six rows have any missing data. The surprise is chest-pain type — asymptomatic patients have a 72.9% disease rate, versus 30.4% for typical angina. They were referred for other reasons, like an abnormal stress test, so they were already sicker. And cholesterol — the textbook risk factor — correlates with disease at just 0.09 in this cohort."

## 2:00–3:00 — Modify (60s)

**[ON SCREEN: notebook — Phase 3 code: ColumnTransformer / Pipeline]**

"Modify is where projects silently cheat, through leakage. If you impute or scale on the whole dataset, test information seeps into training. So everything lives inside a pipeline fitted on train only: question marks become NaN, median imputation for the two columns with missing values, one-hot encoding for chest-pain type, ECG, and ST slope, scaling for logistic regression only. I dropped no variables — with 13 predictors, dropping cholesterol on a weak correlation would risk losing signal that matters in combination. The target was binarized: 0 is no disease, 1 to 4 collapsed into disease present."

## 3:00–4:10 — Model (70s)

**[ON SCREEN: model comparison table from the notebook]**

"Model: three learners. Logistic Regression as the interpretable baseline. A tuned Random Forest — 200 trees, max depth 8, found by a small 12-combination grid search. And HistGradientBoosting, standing in for SEMMA's Neural Network node — a real neural net would be over-parameterised on 303 rows, and I'd rather say that than pretend otherwise. Cross-validation on the training set actually ranks Logistic Regression first, at 0.9037."

## 4:10–5:20 — Assess (70s)

**[ON SCREEN: ROC curves chart; then confusion matrices]**

"Assess, and here is the honest part. On the 61-patient test set: Logistic Regression, AUC 0.960. Random Forest, 0.961. HistGradientBoosting, 0.963. That 0.002 gap is one-fifth of one patient — it is noise, not a win. The Random Forest and gradient boosting make literally identical errors: one missed case out of 28, four false alarms out of 33. So there is no winner; there is a tie. I recommend the Random Forest as the prototype — joint-best accuracy, precision, recall and F1, plus feature importances — with gradient boosting as challenger. Calibration looks sensible at the extremes and thin in the middle, and the subgroup fairness check is reported but cannot prove fairness with six patients in the oldest group."

**[ON SCREEN: feature importance bar chart — thal, ca, cp_4.0 on top]**

"Feature importance backs up the exploration: thallium result, number of vessels, asymptomatic chest pain, max heart rate, ST depression."

## 5:20–6:00 — Wrap-up (40s)

**[ON SCREEN: repo file list — notebook, report.md, medium-article.md, data dictionary]**

"So: SEMMA done end to end, every number traceable to executed code, and the two lessons that matter — state your sampling bias before your results, and say 'it's a tie' when it is one. The executed notebook, the full report, the data dictionary, and a Medium draft of this story are all in the repo linked below. Thanks for watching."

---

**Recording notes:** Record the notebook in Colab (Run all, then scroll phase by phase). Keep the disclaimer slide visible during the Assess segment. Total script ≈ 850 words ≈ 6 minutes at ~140 wpm.
