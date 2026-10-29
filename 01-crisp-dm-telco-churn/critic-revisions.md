# Critic Revision Log — CRISP-DM Telco Churn

## Critic persona prompt (used for all three rounds)

> You are a world-renowned authority on CRISP-DM, author of award-winning books on data mining methodology, a keynote speaker who has taught the CRISP-DM process to thousands of practitioners and reviewed hundreds of CRISP-DM projects. Be brutally honest. For each section of this project, give a score out of 10, list every concrete flaw you find — vague success criteria, skipped subtasks, unjustified preprocessing choices, leakage risks, metrics that flatter the model, missing deployment or ethics content — and say exactly what must change. Do not praise what is merely adequate.

Method: after each round of criticism, I re-checked the notebook, the executed outputs, and the report against the specific flaws named, fixed them, and re-scored only on the basis of what was actually re-verified. No score below was assigned without a corresponding check.

## Round 1 — first full draft reviewed

**Scores:** Business Understanding 5/10 · Data Understanding 6/10 · Data Preparation 6/10 · Modeling 7/10 · Evaluation 5/10 · Deployment 4/10.

**Issues found and fixes made:**
1. *Business success criteria were vague* ("build a good churn model"). Fixed: added explicit, pre-agreed criteria — ROC-AUC ≥ 0.80, recall on churners ≥ 0.70, top-decile lift > 2 — written in Phase 1 before any modelling, and evaluated against them in Phase 5.
2. *Data-quality section claimed "no missing values" from `df.isna().sum()` alone.* The critic flagged this as the classic Telco trap. Fixed: found the real defect — `TotalCharges` stored as object with 11 blank strings, all tenure-0 rows — documented it in Phase 2 and in the data-quality report, and fixed it in Phase 3 with the fill-with-0 rationale.
3. *No business-impact translation — metrics without money.* Fixed: added §5.4 in the notebook and the report, computed from the best model's actual test predictions (TP = 293, FP = 288, FN = 81) under stated assumptions ($65/mo, 12-month horizon, 20% save rate): 59 customers / $45,708 on the test set, ~293 customers / ~$228,540 scaled to the full base.
4. *Deployment was a paragraph of good intentions.* Fixed: wrote a concrete deployment plan (monthly batch scoring, saved pipeline artifact, threshold 0.50, top-decile prioritisation, ownership split) plus monitoring triggers (ROC-AUC < 0.75 alert, PSI > 0.2 investigate / > 0.25 retrain, quarterly retraining).
5. *No ethics content at all.* Fixed: added the fairness check — senior citizens churn at 41.68% vs 23.61%, gender near-identical — with mitigations (offer-only use, per-group error-rate audits at retrain, drop the sensitive feature if over-flagging appears) and an explicit statement that no fairness beyond what was measured is claimed.

## Round 2 — revised draft reviewed

**Scores:** Business Understanding 8/10 · Data Understanding 8/10 · Data Preparation 8/10 · Modeling 8/10 · Evaluation 7/10 · Deployment 7/10.

**Issues found and fixes made:**
1. *Class-imbalance handling was unjustified — "no SMOTE" was asserted, not argued.* Fixed: added the reasoning (26.5% minority is not rare enough to justify synthetic data; `class_weight='balanced'` suffices) and the leakage rule that SMOTE, if ever used, must be fit on the training fold only.
2. *Scaling was applied inconsistently and unexplained.* Fixed: documented that `StandardScaler` is used only inside the Logistic Regression pipeline (trees don't need it), with separate `pre_scaled` / `pre_plain` preprocessors.
3. *Evaluation reported metrics but no confusion matrices and no lift.* Fixed: added all three confusion matrices, the top-decile lift calculation (75.71% churn rate, 2.85× lift), and the ROC-curve chart.
4. *Feature importance was Random Forest only; the "best model" was Logistic Regression, whose drivers were never shown.* Fixed: added the top positive/negative logistic coefficients alongside the Random Forest importances, including the honest note that the MonthlyCharges coefficient is negative only after controlling for TotalCharges.
5. *The critic caught a real modelling subtlety I had glossed over: "best model" was declared by ROC-AUC while Random Forest had the better F1 (0.6211 vs 0.6136).* Fixed: stated this trade-off explicitly in the report — Logistic Regression is the deployed model because ROC-AUC was the pre-agreed primary metric, plus interpretability — instead of pretending the choice was unanimous.

## Round 3 — final review

**Scores:** Business Understanding 9/10 · Data Understanding 9/10 · Data Preparation 9/10 · Modeling 9/10 · Evaluation 9/10 · Deployment 8/10.

**Issues found and fixes made:**
1. *Deployment still lacked a verifiable artifact — "saved model" was claimed but not demonstrated.* Fixed: the notebook now saves `artifacts/best_model.pkl` and smoke-tests it with a reusable `score_customers()` function on the first 5 test customers (probabilities 0.118, 0.852, 0.146, 0.660, 0.060), printed in the executed output.
2. *Every number in the report was re-checked against the executed notebook output* (metrics table, confusion matrices, segment churn rates, lift, business-impact arithmetic: 0.20 × 293 = 58.6 → 59 saved; 58.6 × $65 × 12 = $45,708; ×5 = $228,540). Two transcription risks were caught and corrected during this check (the scaled customer count is 293, from 58.6 × 5, not 59 × 5 = 295).
3. *Remaining critic note (accepted, not fixed):* Deployment scores 8/10, not 10, because the pipeline has not been run against a live monthly extract or a real retention pilot — the save rate is still an assumption and drift monitoring is a plan, not an observed behaviour. That is a genuine limitation of a coursework project and is stated as such in the report rather than papered over.

**Final verdict (Round 3):** all six CRISP-DM phases present, each with its subtasks completed and evidenced in the executed notebook; success criteria set before modelling and met (ROC-AUC 0.8416 ≥ 0.80, recall 0.7834 ≥ 0.70, lift 2.85× > 2); no invented numbers — every figure traces to executed notebook output.
