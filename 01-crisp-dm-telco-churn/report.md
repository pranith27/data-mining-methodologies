# CRISP-DM Project Report — Predicting Telco Customer Churn

**Author:** Pranith Varma Pakalapati — CMPE 256, San Jose State University
**Methodology:** CRISP-DM (Cross-Industry Standard Process for Data Mining), all 6 phases
**Dataset:** Telco Customer Churn (IBM sample), 7,043 customers × 21 columns
**Source:** https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
**Notebook:** `CRISP_DM_Telco_Churn.ipynb` (executed top-to-bottom; 23 cells, 14 code cells, 0 errors)
**Seed:** 42 everywhere. **Split:** stratified 80/20 (5,634 train / 1,409 test).

## Executive summary

A telecom operator loses 26.54% of its customers (1,869 of 7,043). We built churn-prediction models following CRISP-DM end to end. The best model, **Logistic Regression, reached ROC-AUC 0.8416** on a held-out test set, beating tuned Random Forest (0.8388) and HistGradientBoosting (0.8362) — all three cleared the pre-agreed success bar of ROC-AUC ≥ 0.80. The model catches 78.3% of churners, and the top risk decile churns at 75.7% — a 2.85× lift over the base rate. Under stated assumptions ($65/month average revenue, 12-month horizon, 20% save rate), scoring the full customer base would retain roughly **293 customers and ~$228,540 of revenue per scoring cycle**. The deliverable is a saved scoring pipeline (`artifacts/best_model.pkl`) with a monthly batch-scoring and monitoring plan.

## Methodology — what CRISP-DM is

CRISP-DM is the de-facto standard process for data mining, with six phases: (1) Business Understanding, (2) Data Understanding, (3) Data Preparation, (4) Modeling, (5) Evaluation, (6) Deployment. The phases are not a waterfall — the process is iterative, and the diagram is usually drawn as a cycle with arrows looping back from later phases to earlier ones (for example, a data-quality problem found in preparation sends the project back to understanding). The methodology was chosen for this project because it forces the business question and success criteria to be fixed *before* any modelling, and because it treats deployment — not a notebook accuracy number — as the end of the project.

## Phase 1 — Business Understanding

**Business problem.** Acquiring a new telecom customer costs far more than retaining one, and the customers who leave are disproportionately high-value: churners pay on average $74.44/month versus $61.27/month for customers who stay.

**Business objectives.** (1) Identify customers at high risk of churning before they leave, so retention offers can be targeted. (2) Understand *why* customers churn so the business can fix root causes. (3) Deliver a scoring pipeline the business can re-run monthly.

**Data-mining goal.** Binary classification: predict `Churn` (Yes/No) from demographics, account and service features.

**Success criteria (set before modelling).** Model: ROC-AUC ≥ 0.80 on held-out data; recall on churners ≥ 0.70. Business: lift > 2 in the top risk decile. Deployment: a reproducible batch-scoring script plus a monitoring plan.

**Risks.** Single historical snapshot (behaviour may drift); no complaint, network-quality or competitor data (some churn drivers unobserved); retention-offer effectiveness is assumed, not measured (20% save rate), and must be validated by a pilot A/B test.

## Phase 2 — Data Understanding

**Collection.** IBM Telco Customer Churn sample dataset, one row per customer. Features: demographics (gender, SeniorCitizen, Partner, Dependents), account (tenure, Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges) and services (PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies). Full definitions in `data/DATA_DICTIONARY.md`.

**Verified facts (all from executed notebook output).**

- Shape 7,043 × 21. No duplicate rows, no duplicate `customerID`s. Pandas reports zero NaNs — but that is misleading (see below).
- Churn rate **26.54%** (1,869 Yes / 5,174 No).
- Tenure: mean 32.37 months, median 29, range 0–72. MonthlyCharges: mean $64.76, range $18.25–$118.75. Senior citizens are 16.2% of customers.
- **Data-quality defect:** `TotalCharges` is stored as text and **11 rows contain a blank string** instead of a number. All 11 have `tenure == 0` (brand-new customers with no charges yet). This is the dataset's only real defect; it is fixed in Phase 3.

**Churn rate by segment (the business story):**

| Segment | Churn rate |
|---|---|
| Contract: Month-to-month / One year / Two year | 42.71% / 11.27% / 2.83% |
| Payment: Electronic check / Mailed check / Bank transfer / Credit card | 45.29% / 19.11% / 16.71% / 15.24% |
| Internet: Fiber optic / DSL / No internet | 41.89% / 18.96% / 7.40% |
| Paperless billing: Yes / No | 33.57% / 16.33% |
| Senior citizen: Yes / No | 41.68% / 23.61% |
| Gender: Female / Male | 26.92% / 26.16% |
| Partner: No / Yes | 32.96% / 19.66% |
| Dependents: No / Yes | 31.28% / 15.45% |

**Churners vs stayers.** Churners have much shorter tenure (mean 17.98 vs 37.57 months; median 10 vs 38) and higher monthly charges ($74.44 vs $61.27). Correlations with churn (0/1): tenure −0.352, MonthlyCharges +0.193, TotalCharges −0.199, SeniorCitizen +0.151. Tenure is the strongest numeric signal; no numeric pair is collinear enough to drop a feature.

## Phase 3 — Data Preparation

- `TotalCharges`: `pd.to_numeric(errors='coerce')` turns the 11 blanks into NaN; filled with **0**, justified because all 11 customers have tenure 0 and genuinely have no charges yet (median-fill would invent ~$1,397 of charges for a brand-new customer). After coercion: float64, 0 remaining NaNs. TotalCharges range $18.80–$8,684.80, mean $2,283.30, median $1,397.48.
- Dropped `customerID` (identifier; no predictive value, leakage risk if memorised).
- Target: `Churn` → 1 = Yes, 0 = No.
- Categorical features (15) → one-hot encoding (`OneHotEncoder(handle_unknown='ignore')`) inside an sklearn `ColumnTransformer`, so scoring reuses the exact same transform.
- Numeric features (4: SeniorCitizen, tenure, MonthlyCharges, TotalCharges) → `StandardScaler` **only for Logistic Regression** (tree models do not need scaling).
- **Class imbalance:** churn is 26.5% — no SMOTE. `class_weight='balanced'` is sufficient and avoids synthetic-data leakage risk. (If SMOTE were ever used, it would have to be fit on the training fold only, never before the split.)
- **Split:** stratified 80/20, `random_state=42` — train 5,634 (churn 26.54%), test 1,409 (churn 26.54%). The test set was touched once, for final evaluation only.

## Phase 4 — Modeling

Three models spanning the interpretability ↔ accuracy trade-off, each wrapped in a pipeline with the Phase-3 preprocessor (no leakage from fitting encoders/scalers on test data):

1. **Logistic Regression** — interpretable baseline. `max_iter=1000`, `class_weight='balanced'`.
2. **Random Forest** — tuned with `GridSearchCV`, 5-fold CV on the training set only, scoring ROC-AUC. Grid: `n_estimators` {200, 300} × `max_depth` {None, 10} × `min_samples_leaf` {1, 2}. Best params: `max_depth=10, min_samples_leaf=2, n_estimators=300`; best CV ROC-AUC **0.8457**.
3. **HistGradientBoosting** — gradient boosting, `class_weight='balanced'`.

## Phase 5 — Evaluation

Test-set results (n = 1,409; churners = 374):

| Model | ROC-AUC | Accuracy | Precision (churn) | Recall (churn) | F1 (churn) |
|---|---|---|---|---|---|
| **Logistic Regression** | **0.8416** | 0.7381 | 0.5043 | 0.7834 | 0.6136 |
| Random Forest (tuned) | 0.8388 | 0.7523 | 0.5229 | 0.7647 | 0.6211 |
| HistGradientBoosting | 0.8362 | 0.7544 | 0.5263 | 0.7487 | 0.6181 |

Confusion matrices ([[TN, FP], [FN, TP]]): Logistic Regression [[747, 288], [81, 293]]; Random Forest [[774, 261], [88, 286]]; HistGradientBoosting [[783, 252], [94, 280]].

**Against the success criteria:** all three models clear ROC-AUC ≥ 0.80; Logistic Regression's recall of 0.7834 clears the ≥ 0.70 bar. **Best model by ROC-AUC: Logistic Regression (0.8416)** — the simplest model won, by a small margin (0.0028 over Random Forest). Its F1 (0.6136) is marginally below Random Forest's (0.6211); the choice of Logistic Regression as the deployed model rests on ROC-AUC (the pre-agreed primary metric) plus its interpretability for the business.

**Lift.** The best model's top risk decile churns at **75.71%** vs a 26.54% base rate — **2.85× lift**, clearing the > 2 business criterion. Targeting the top decile is nearly three times as efficient as contacting customers at random.

**What drives churn.** Random Forest importances (top 5): tenure 0.1264, Contract_Month-to-month 0.1253, TotalCharges 0.1030, MonthlyCharges 0.0711, Contract_Two year 0.0629; followed by OnlineSecurity_No (0.0560), InternetService_Fiber optic (0.0471), TechSupport_No (0.0463), PaymentMethod_Electronic check (0.0369). Logistic Regression coefficients agree on direction: tenure −1.154 and Contract_Two year −0.776 push strongly toward staying; Fiber optic +0.708 and Month-to-month +0.658 push toward churning. (MonthlyCharges has a negative coefficient, −0.676, *after controlling for* TotalCharges (+0.490) — a reminder that coefficients are conditional associations, not standalone effects.)

**Business impact — computed from the best model's actual test predictions, assumptions stated explicitly.** Assumptions: average revenue $65/month per customer; 12-month horizon; 20% of correctly flagged churners are saved by a retention offer. Test set: TP = 293 churners correctly flagged, FP = 288 false alarms, FN = 81 churners missed. Customers saved on the test set: 59 (20% of 293); revenue retained: **$45,708 over 12 months**. Scaled to the full customer base (test = 20% of the data, ×5): **~293 customers saved, ~$228,540 revenue retained per scoring cycle**. Revenue at risk from the 81 missed churners on the test set: $63,180 over 12 months. The 20% save rate is an assumption, not a measurement — a pilot A/B test is required before quoting ROI.

## Phase 6 — Deployment

**Deployment plan.** Monthly batch scoring: a script loads the saved best model (`artifacts/best_model.pkl`, Logistic Regression pipeline) and the current customer extract, applies the same pipeline (encoding/scaling inside the pipeline, so no separate preprocessing step can drift out of sync), scores every active customer, and writes `customer_id, churn_probability, risk_band` for the retention team. High-risk = probability ≥ 0.50 (the threshold used in evaluation); the top decile gets the retention offer first. Retention action is matched to the customer's drivers (contract-upgrade discount, payment-method switch incentive, fibre-support check-in), not a generic discount. Data science owns the model; retention owns the intervention; both review results monthly. A reusable `score_customers()` function is in the notebook and smoke-tested on the first 5 test customers (probabilities 0.118, 0.852, 0.146, 0.660, 0.060).

**Monitoring.** Track ROC-AUC and recall on each new month's realised churn (labels arrive with a lag); alert if ROC-AUC falls below 0.75. Compute Population Stability Index (PSI) on tenure, MonthlyCharges and contract mix monthly; PSI > 0.2 triggers investigation, PSI > 0.25 triggers retraining. Retrain at least quarterly, or sooner if a new plan or pricing change ships. Re-check the fairness audit at every retrain.

**Ethics & fairness (checked, not assumed).** Churn rates differ by sensitive attributes in the raw data: senior citizens churn at 41.68% vs 23.61% for non-seniors; gender is near-identical (female 26.92% vs male 26.16%). The model uses `SeniorCitizen` and `gender` as inputs, so it can learn those gaps. Mitigations: (a) the score is used only to *offer* retention help, never to deny service or raise prices; (b) audit false-positive / false-negative rates by senior-citizen status and gender at each retrain; (c) if a retrain shows a group being systematically over-flagged, drop the sensitive feature and re-check performance. No fairness claim is made beyond what was measured here.

**Limitations.** Single snapshot with no time dimension; no interaction, complaint, network-quality or competitor data; the 20% save rate is assumed; the model predicts churn, it does not prove *why* a customer churns.

**Next steps.** (1) Pilot A/B test of the retention offer on the top decile for one month; measure the true save rate. (2) Add tenure-binned and contract-expiry features; test probability calibration. (3) Move batch scoring into a scheduled job; add a PSI drift dashboard. (4) Revisit whether `SeniorCitizen` should remain a model input after the fairness audit.

## Reproducibility

- Notebook: `CRISP_DM_Telco_Churn.ipynb` — 23 cells (14 code), executed top-to-bottom with `jupyter nbconvert --execute`, 0 errors, outputs saved.
- Environment: Python 3.12, scikit-learn 1.9.1, pandas 2.1.4, matplotlib, seaborn (`requirements.txt`).
- Data: `data/Telco-Customer-Churn.csv` (7,043 rows), downloaded from the IBM GitHub URL in the notebook itself (local copy used if present).
- Artifacts: `artifacts/best_model.pkl` (saved Logistic Regression pipeline), `artifacts/chart_churn_by_contract.png`.
- Note: the shared venv needed `matplotlib-inline==0.1.6` (downgraded from 0.2.2) because 0.2.2 is incompatible with matplotlib 3.6.3 in that environment (`RcParams` has no `_get`); this affects local execution only, not Colab.
