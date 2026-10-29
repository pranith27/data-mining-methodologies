# Video Script — CRISP-DM Telco Churn Walkthrough (6 minutes)

**Format:** screen-recorded walkthrough of the executed Colab notebook + report. One take per segment; show the notebook, not slides.

## 0:00–0:35 — Hook (show: notebook title cell)
**Say:** "One in four customers left this telecom company — 1,869 out of 7,043 — and the ones who left were paying the most, 74 dollars a month versus 61 for the customers who stayed. In this video I'll show you how I predicted who leaves next, using CRISP-DM — all six phases, one dataset, three models, and a deployment plan at the end."

## 0:35–1:15 — Phase 1: Business Understanding (show: Phase 1 markdown)
**Say:** "CRISP-DM starts with the business, not the model. The goal: flag customers before they churn so retention can act. And before I trained anything, I wrote down what 'good' means — ROC-AUC of at least 0.80, and recall of at least 0.70 on churners, because missing a leaver costs more than a false alarm. If you don't fix the target first, you'll move it later."

## 1:15–2:20 — Phase 2: Data Understanding (show: EDA outputs + contract chart)
**Say:** "The data is the IBM Telco Churn sample — 7,043 customers. The first thing you notice: month-to-month contracts churn at 42.7 percent, two-year contracts at 2.8 percent. Electronic-check payers, 45 percent. Fibre-optic customers, 42 percent. And churners are new — median tenure ten months versus 38 for stayers. Also, pandas says there are zero missing values — which is wrong. TotalCharges is stored as text, and eleven rows are blank strings. All eleven are brand-new customers with zero tenure. That's the kind of defect Phase 2 exists to catch."

## 2:20–3:05 — Phase 3: Data Preparation (show: preparation code cell + split output)
**Say:** "Preparation: coerce TotalCharges to numeric and fill those eleven blanks with zero — they genuinely have no charges yet, so inventing the median would be wrong. Drop the customer ID. One-hot encode the categoricals, scale only for logistic regression, and split 80/20 stratified, seed 42 — train 5,634, test 1,409, same churn rate in both. No SMOTE: at 26.5 percent churn, class weights are enough, and synthetic data would only add leakage risk."

## 3:05–4:05 — Phase 4–5: Modeling & Evaluation (show: metrics table + ROC curves)
**Say:** "Three models: Logistic Regression, a Random Forest tuned by grid search — 300 trees, depth 10, cross-validated AUC 0.8457 — and HistGradientBoosting. Here is the surprise: the simplest model won. Logistic Regression, ROC-AUC 0.8416, ahead of the forest at 0.8388. All three cleared the 0.80 bar, and logistic catches 78 percent of churners. The top risk decile churns at 75.7 percent — nearly three times the base rate. And the drivers are exactly what the EDA hinted: tenure, contract type, total charges."

## 4:05–4:50 — Business impact (show: lift / business-impact output)
**Say:** "Metrics don't pay bills, so here's the money, computed from the model's actual test predictions — 293 churners correctly flagged. Assume 65 dollars a month, a 12-month horizon, and that a retention offer saves 20 percent of the people we flag. That is about 293 customers and roughly 228,000 dollars of revenue per scoring cycle across the full base. The 20 percent is an assumption, not a measurement — it needs a real pilot. But even at half that, the case is obvious."

## 4:50–5:35 — Phase 6: Deployment & ethics (show: Phase 6 markdown + scoring function)
**Say:** "A notebook is not a deployment. The model is saved as a pipeline, with a scoring function the team can run monthly on new customers, and monitoring rules: alert if AUC drops below 0.75, investigate if drift exceeds 0.2, retrain quarterly. And the ethics check: senior citizens churn at 41.7 percent versus 23.6, and the model sees that feature — so the score is used only to offer help, never to deny service, and error rates by group get audited at every retrain."

## 5:35–6:00 — Close (show: repo file list)
**Say:** "Six phases, one honest result: the explainable model won, the contract table told most of the story before any modelling, and the deliverable is a pipeline a team can run — not just an accuracy number. Links to the notebook, report, and code are in the description. Thanks for watching."
