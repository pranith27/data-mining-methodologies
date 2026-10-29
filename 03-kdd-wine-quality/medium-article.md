# What 1,599 Wines Taught Me About Quality — A KDD Story

## The question a winery actually asks

A winemaker does not ask, "Can a machine predict a wine score?" They ask something more practical: *which of the things I can measure in the lab actually move the score a tasting panel gives my wine?* If alcohol, acidity and sulphur really drive quality, the winery can steer fermentation, blending and sulphur dosing with data instead of taste alone. If they don't, the lab numbers are decoration.

That is a knowledge-discovery question, not just a modelling question. So I ran it through KDD — Knowledge Discovery in Databases, the five-step process Fayyad, Piatetsky-Shapiro and Smyth laid out in 1996 — on the UCI Wine Quality dataset: 1,599 red wines from Portugal's Vinho Verde region, each with eleven physicochemical measurements and one sensory score from a trained panel. Everything that follows comes from code I ran, not from intuition. The numbers are the ones the notebook produced.

## KDD, in sixty seconds — and how it differs from CRISP-DM and SEMMA

If you have taken a data mining course, you have met three methodologies that look similar and are not. CRISP-DM is a business-first project framework: six phases starting with *business understanding*, built for commercial data mining projects with stakeholders and deployment plans. SEMMA is SAS's five-step workflow — Sample, Explore, Modify, Model, Assess — pragmatic, tool-shaped, and strongest as a modelling loop. KDD is the oldest and most academic of the three, and it is the one this project follows. Its five steps are Selection, Preprocessing, Transformation, Data Mining, and Interpretation/Evaluation — and the crucial difference is in the name. In KDD, data mining is *one step inside a larger process of discovering knowledge*. The deliverable is not a model. The deliverable is knowledge a human can act on, with its limits stated. That is why the last step — interpretation — gets as much space here as the modelling.

## Step 1: Selection — choosing the question and the data

The goal was fixed first: discover what drives perceived quality in red wine. Two targets were defined, because the winery has two questions. The primary task is regression on the quality score itself (observed range 3 to 8 on a 0–10 scale). The secondary task is classification: is this wine premium, defined as quality 7 or above? Only 13.6 percent of the wines clear that bar, so the second task is an imbalanced problem from the start, and that shapes every metric choice later.

One deliberate exclusion: the UCI source also ships a white-wine file with 4,898 rows. I left it out. Red and white wines have different chemistry baselines — reds carry far more volatile acidity, whites more residual sugar — and a combined model would spend its capacity learning "red versus white" instead of "good versus bad". The findings here are about red wine, period.

## Step 2: Preprocessing — the data-quality audit

Before any modelling, the data gets audited, and the audit is part of the deliverable. The good news: zero missing values in all twelve columns. The bad news: 240 of the 1,599 rows — 15 percent — are exact duplicates. Identical rows can land on both sides of a train/test split and quietly leak the test set, so they were dropped, leaving 1,359 unique wines. The target distribution barely moved, which is reassuring: the duplicates were not concentrated in any one score.

Then the shapes. Five features are strongly right-skewed: chlorides (skew 5.68), residual sugar (4.54), sulphates (2.43), total sulphur dioxide (1.52) and free sulphur dioxide (1.25). The IQR outlier counts are large — 155 for residual sugar, 112 for chlorides — but these are real wines, not sensor errors. A red with 15.5 grams per litre of residual sugar is a genuine sweet red. So the outliers stayed; the skew was handled later with a log transform instead.

Even before modelling, the correlations told a story. Alcohol correlates with quality at +0.48, the strongest positive signal. Volatile acidity is the strongest negative at −0.39. Sulphates (+0.25) and citric acid (+0.23) help. And the variable a casual drinker would bet on — residual sugar — sits at +0.01. Essentially zero. For these dry reds, sweetness does not move the panel score at all.

## Step 3: Transformation — shaping the data for mining

Three new features were engineered, each justified by wine chemistry rather than by fishing for signal. Total acidity sums the three acids, because acidity is experienced as a whole. The sulphur ratio — free SO₂ divided by total SO₂ — measures how much of the dosed sulphur is actually active and protective. And an alcohol × volatile acidity interaction term tests whether alcohol masks vinegar-like faults or compounds them. Whether these features help was tested, not assumed — more on that below.

The skewed features got a log1p transform. Standardisation was applied only for the linear models, which need it; the tree models got the log-transformed features raw. All of this lives inside scikit-learn pipelines fit on the training set only, so nothing about the test set leaks into the transformations. The split is 80/20, stratified so the rare premium class keeps its share in both halves, seed 42.

## Step 4: Data mining — five models, two tasks

For the regression task I ran Linear Regression as the interpretable baseline, a Random Forest, and a HistGradientBoosting regressor. The forest won: R² of 0.43, RMSE 0.64, MAE 0.49, against 0.35 for the linear model and 0.38 for gradient boosting. Light tuning — a small grid search over tree count, depth and leaf size — found max depth 10, minimum leaf 5, 500 trees, and bought almost nothing: R² moved from 0.428 to 0.430. That is itself a finding. The default forest was already near this dataset's ceiling, and heavier tuning would have been overfitting the validation folds.

For the premium classification task, Logistic Regression and a Random Forest both reached ROC-AUC around 0.89–0.90, with near-identical F1 scores of about 0.51. Accuracy is deliberately not the headline here: predicting "not premium" for every wine would score 86 percent and learn nothing. The interesting difference is the trade-off. Logistic Regression catches 86 percent of premium wines but raises 56 false alarms (precision 36 percent). The Random Forest is balanced: 55 percent precision, 49 percent recall. Same ranking ability, different operating point — and the choice between them belongs to the winery, not the algorithm.

And the engineered features? The same forest without them scored R² 0.419; with them, 0.428 — a gain of 0.009. Real, small, and worth reporting honestly rather than overselling.

## Step 5: Interpretation — turning patterns into knowledge

This is the step KDD exists for, and it is where the project earns its keep. Three findings held up across every method I tried — correlation, linear coefficients, and tree importance all agree.

First, alcohol dominates. It carries a third of the Random Forest's total importance (0.33), the largest standardised linear coefficient (+0.40), and the binned means are monotone: wines at 8–9.5 percent alcohol average 5.23; wines above 11 percent average 6.20 — nearly a full quality point. Mean alcohol climbs steadily with score, from 9.9 percent for score-5 wines to 12.2 percent for score-8 wines.

Second, volatile acidity is the quality killer. Wines below 0.40 grams per litre average 6.05; above 0.70, they average 5.17. The worst wines in the dataset, those scoring 3, average more than twice the volatile acidity of the best (0.89 versus about 0.41). That is the vinegar fault, and trained tasters penalise it exactly as the textbooks say they should.

Third, sulphates and citric acid help — sulphates rise from a 5.23 average below 0.55 g/L to 6.01 above 0.80 — while residual sugar does nothing. That last one matters because it corrects a folk belief: for dry reds, sweetness is not what the panel rewards.

The error analysis is as informative as the accuracy. The model is systematically conservative at the extremes: it over-predicts the worst wines by 1.66 points on average and under-predicts the best by 1.54, while nailing the crowded middle (scores 5 and 6) to within 0.36–0.40. Almost ninety percent of predictions land within one point of the truth. So trust the model for ranking ordinary batches; do not trust it to spot a once-in-a-decade wine or to condemn a batch on its own.

And the honest ceiling: even the best model explains only 43 percent of the variance. The remaining 57 percent is taster subjectivity and things this dataset never measured — grape variety, vintage, tannin structure. That is not a modelling failure. It is knowledge about where the knowledge stops.

## Deployment: what a winery does with this

The model ships as a simple QC screen. Every finished batch's lab panel goes through the tuned forest; batches predicted below 5 get a human re-taste before release, and batches predicted above 6.5 get fast-tracked for premium review. Blending guidance is directional only: protect alcohol, keep volatile acidity low, don't over-dose total SO₂ — then rank candidate blends by predicted quality and taste-test the top few. Never auto-approve a blend on a model score.

Monitoring is monthly: if a new vintage or supplier shifts the incoming lab measurements, re-validate on a fresh labelled sample and retrain when performance drops. And because the target is human judgement, a new tasting panel is effectively a new target — the model gets re-validated when the panel changes.

## The limits, stated plainly

Three things this project does not claim. It does not transfer to white wine or other regions without re-validation — Vinho Verde reds only. It does not establish causation — alcohol correlates with quality largely because it tracks grape ripeness, and adding alcohol to a wine will not make it better. And it is not a recipe. Anyone selling you a formula for a 90-point wine from eleven lab measurements is selling something else.

## The takeaway

KDD's promise is not a better leaderboard score. It is a process that ends with knowledge you can defend: alcohol drives perceived quality, volatile acidity destroys it, sugar is irrelevant for dry reds, and a little over half of what tasters taste is not in the lab data at all. That last sentence is the most valuable output of the whole project. A methodology that forces you to write it down is doing its job.

*Dataset: Cortez et al. (2009), UCI Machine Learning Repository. Methodology: Fayyad, Piatetsky-Shapiro & Smyth (1996), "From Data Mining to Knowledge Discovery in Databases", AI Magazine 17(3). All code and results: see the project repository.*
