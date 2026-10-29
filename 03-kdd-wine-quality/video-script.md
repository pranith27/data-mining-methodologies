# Video Script — KDD Wine Quality Walkthrough (6 minutes)

**Format:** Screen-recorded YouTube walkthrough of `KDD_Wine_Quality.ipynb` in Google Colab.
**Target length:** 6:00. **Tone:** Direct, no filler. Every number spoken is from the executed notebook.

---

## [0:00–0:25] Hook — on screen: title slide, "What Makes a Good Red Wine?"

**Say:** "A winery can measure eleven things about a wine in the lab. The question is which of them actually move the score a tasting panel gives it. I ran 1,599 red wines through the full KDD process — Knowledge Discovery in Databases — and the answer is not what most people guess. Sugar, for example, does nothing. Here is the whole project, step by step."

**On screen:** Colab notebook open at the title cell; dataset name and 1,599-row count visible.

---

## [0:25–1:05] What KDD is — on screen: the 5-step diagram in the notebook intro

**Say:** "Quick context. KDD is the 1996 Fayyad process: Selection, Preprocessing, Transformation, Data Mining, and Interpretation. The key idea — and what separates it from CRISP-DM and SEMMA — is that data mining is just one step inside it. The deliverable is not a model, it is knowledge, with its limits stated. CRISP-DM starts from business understanding and is built for commercial projects; SEMMA is SAS's modelling loop. KDD is the academic original, and this project follows it exactly."

**On screen:** Scroll through the notebook's KDD overview; highlight the five step headings.

---

## [1:05–2:00] Step 1 & 2: Selection and Preprocessing — on screen: data load + EDA outputs

**Say:** "Step one, Selection. UCI Wine Quality, red wine only — I excluded the white wines deliberately, because reds and whites have different chemistry and a combined model would just learn red-versus-white. Two targets: regression on the quality score, and a binary premium task, quality seven or above — only 13.6 percent of wines clear that bar.
Step two, Preprocessing. Zero missing values — good. But 240 rows, 15 percent of the data, are exact duplicates, so they go: identical rows can leak across the train-test split. That leaves 1,359 unique wines. Five features are heavily skewed — chlorides at 5.7, residual sugar at 4.5 — and there are over a hundred IQR outliers on sugar and chlorides. Those stay, because they are real wines, not sensor errors."

**On screen:** Quality distribution bar chart; skew table; the duplicate-drop output showing 1,599 → 1,359.

---

## [2:00–2:50] Step 3: Transformation — on screen: feature engineering + split cells

**Say:** "Step three, Transformation. Three engineered features, each with a chemistry reason, not a fishing expedition. Total acidity — the sum of the three acids. A sulphur ratio — free over total SO₂ — measuring how much dosed sulphur is actually active. And an alcohol-times-volatile-acidity interaction, to test whether alcohol masks vinegar faults. Skewed features get a log transform, everything goes through pipelines fit on the training set only — no leakage — and the split is 80-20, stratified, seed 42."

**On screen:** The `add_features` function; the pipeline definition; train 1,087 / test 272 output.

---

## [2:50–4:10] Step 4: Data Mining — on screen: model leaderboards

**Say:** "Step four, the mining itself. Regression first: Linear Regression gets R² 0.35. HistGradientBoosting, 0.38. Random Forest, 0.43, with an RMSE of 0.64. Light tuning — a small grid search — finds depth 10, 500 trees, and buys almost nothing: 0.428 to 0.430. That tells you the data, not the tuning, is the ceiling.
Classification, premium versus not: both models hit ROC-AUC around 0.89 to 0.90. Logistic Regression catches 86 percent of premium wines but with only 36 percent precision — 56 false alarms. The Random Forest is balanced, 55 percent precision, 49 percent recall. Same ranking ability, different trade-off, and the winery picks the operating point, not the algorithm.
And the engineered features? They add 0.009 to R². Real, small, and honestly reported."

**On screen:** Regression leaderboard table; classification table with both confusion matrices; the +0.0089 delta output.

---

## [4:10–5:15] Step 5: Interpretation — on screen: importance chart + binned tables

**Say:** "Step five is where KDD earns its keep. Alcohol is the dominant driver — a third of the Random Forest's importance, correlation plus 0.48. Wines above 11 percent alcohol average 6.20; wines under 9.5 percent average 5.23 — nearly a full quality point. Volatile acidity is the killer: below 0.40 grams per litre, wines average 6.05; above 0.70, 5.17. Sulphates and citric acid help. And residual sugar — the thing everyone guesses — correlates at 0.01. Nothing.
The error analysis matters too. The model is conservative at the extremes: it over-predicts the worst wines by 1.66 points and under-predicts the best by 1.54, while nailing the middle. Eighty-nine percent of predictions land within one point. And the honest ceiling: 57 percent of the variance is not in the lab data at all — taster subjectivity, grape, vintage. That is knowledge, too."

**On screen:** Feature importance bar chart; binned alcohol / volatile acidity / sulphates tables; residual plot and error-by-score table.

---

## [5:15–5:50] Deployment — on screen: the predict_quality demo cell

**Say:** "Finally, deployment. The shipped model is the tuned forest refit on all 1,359 wines, wrapped in a predict function a QC script can call. A good-profile wine — 12.5 percent alcohol, low volatile acidity — scores 6.89, premium likely. A faulty profile — 9 percent alcohol, volatile acidity 1.1 — scores 4.56. The winery uses it as a screen: flag low predictions for a human re-taste, fast-track high ones for premium review, and re-validate monthly, because a new tasting panel is effectively a new target. And three limits, stated plainly: sensory scores are subjective, this is one region and one style, and correlation is not causation — adding alcohol to a wine will not make it better."

**On screen:** Run the deployment cell live; show the two predictions (6.89 vs 4.56).

---

## [5:50–6:00] Close — on screen: conclusion cell + repo file list

**Say:** "So: alcohol drives quality, volatile acidity destroys it, sugar is irrelevant for dry reds, and a little over half of what tasters taste is not in the lab data. The notebook, the full report, the data dictionary and the code are all in the repo linked below. Thanks for watching."

**On screen:** Repository folder listing; end card.
