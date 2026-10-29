# I Ran a 1980s Heart Dataset Through SEMMA — and the Models Tied

*How SAS's five-step methodology holds up on 303 patients, why the "best model" was a statistical tie, and what the data refused to say.*

## The patient with no chest pain was the sickest one

That is the first thing the data told me, and it is the kind of sentence that makes you double-check your code. In the UCI Heart Disease dataset — 303 patients examined at the Cleveland Clinic in the 1980s — the patients whose chest pain was classified as *asymptomatic* had a heart-disease rate of 72.9%. The patients with textbook typical angina? 30.4%.

It feels backwards until you think about how the data were collected. These were not random members of the public. They were people referred for cardiac evaluation, and the asymptomatic ones were referred for other reasons — an abnormal stress test, a suspicious ECG — which meant something was already wrong. The dataset is a lesson in selection bias before it is a lesson in machine learning, and that is exactly why I chose it for this project: to run a complete, phase-by-phase SEMMA analysis, and to be honest about every place where the methodology — and the data — stopped short.

## What SEMMA is, and how it differs from CRISP-DM

SEMMA stands for **Sample, Explore, Modify, Model, Assess**. It was developed for SAS Enterprise Miner, and it is the most model-centric of the classic data-mining methodologies. CRISP-DM, the better-known framework, begins with business understanding and ends with deployment; SEMMA assumes the problem is already defined and concentrates on the journey from raw data to an assessed model. Five phases, no ceremony.

That focus is both its appeal and its blind spot. SEMMA will not ask you whether the problem is worth solving, and it has no deployment phase — the monitoring plan at the end of this project is something I added myself, borrowed from CRISP-DM thinking. What SEMMA does give you is a tight, repeatable discipline: sample honestly, explore before you model, modify without leaking, model more than one way, and assess like someone is going to check your work.

One tooling note, because honesty matters here: SEMMA was born in SAS Enterprise Miner, and I had no SAS licence for this project. Every step is implemented in Python with scikit-learn, and every phase names its SAS-equivalent node — Data Partition, StatExplore, Impute, Regression, Model Comparison — so the mapping is explicit. The logic is what is being demonstrated, not the vendor tool.

## The dataset

The Cleveland processed set: 303 rows, 14 attributes, no header row, missing values coded as the character `?`. The target is a 0–4 severity scale — 0 means no disease, 1–4 mean disease of increasing severity. I binarized it to 0/1 (disease present or not), because the smallest severity class has only 13 patients, far too few to model. That gives 164 healthy patients and 139 with disease: a prevalence of 45.87%.

That prevalence is the first warning sign. In the general adult population, heart disease prevalence is in the low single digits. 45.9% tells you this is a referral population — sick people sent to a specialist clinic — and any model trained here describes *that* population, not yours or mine. Add that the cohort is 68% male, from a single hospital, in a single decade, and the generalizability limits write themselves.

## Phase 1: Sample — the smallest honest decision

With 303 rows, down-sampling would be vandalism, so I did not do it. The Sample phase became a careful partition instead: a stratified 80/20 train/test split (242 train, 61 test, seed 42), with stratification holding the 45.9% disease rate identical in both parts, plus 5-fold stratified cross-validation on the training set so no model would be chosen on the basis of one lucky split. That is the whole phase — and its most important output is not a number but a paragraph of caveats about who these patients were.

## Phase 2: Explore — let the data argue first

Exploration found a clean dataset with a few quirks. Only six rows have any missing value at all — four in `ca` (number of major vessels seen on fluoroscopy) and two in `thal` (a thallium stress-test result). Outliers exist but are physiologically plausible: five cholesterol readings above the IQR fence, including one at 564 mg/dl, and nine high resting blood pressures up to 200 mm Hg. In cardiac patients, these are real people, not data errors, so I kept them.

The correlations were the interesting part. Exercise-induced angina (+0.43), ST depression (+0.43), and chest-pain type (+0.41) correlate most strongly with disease; maximum heart rate correlates negatively (−0.42) — sicker hearts cannot go as fast. And cholesterol, the textbook risk factor, correlates at just +0.09. In this cohort, cholesterol alone barely separates the sick from the healthy. That is not a claim about cholesterol in general; it is a reminder that correlation in one small 1980s referral cohort is not a causal claim, and that dropping variables on univariate correlation alone would be a mistake.

The subgroup rates told the story: disease in 55.3% of men vs 25.8% of women; 76.8% of patients with exercise-induced angina vs 30.9% without; 76.1% with a reversible thallium defect vs 22.3% with a normal result. And age: disease rises from 25.4% in the 29–45 group to 62.2% in the 56–65 group.

## Phase 3: Modify — the phase where cheating happens

Modify is where most data-science projects silently go wrong, because it is where leakage lives. If you impute missing values or scale features using the whole dataset, information from your test set seeps into training, and your test scores become fiction. So every transformation here lives inside a scikit-learn pipeline fitted on training data only: `?` becomes NaN, median imputation for `ca` and `thal`, one-hot encoding for the nominal variables (chest-pain type, ECG result, ST slope), and standard scaling for the logistic regression pipeline only — tree models do not need it.

I dropped no variables. With 13 predictors and 303 rows, discarding cholesterol because its correlation looked weak would risk throwing away signal that matters in combination. The feature-importance ranking in the Assess phase would later audit that decision — and it did, with cholesterol contributing meaningfully to the Random Forest.

## Phase 4: Model — three ways to answer the same question

Three models, chosen to span the interpretability–flexibility spectrum: Logistic Regression (the interpretable baseline, whose coefficients read as log-odds), a tuned Random Forest (the non-linear workhorse), and HistGradientBoosting (gradient boosting, standing in for SEMMA's Neural Network node — a genuine neural network would be over-parameterised on 303 rows, and I would rather state that substitution than pretend otherwise).

The Random Forest got light tuning — a 12-combination grid search settling on 200 trees, max depth 8, minimum leaf size 2, with a cross-validated ROC-AUC of 0.8918. Small grid, deliberately: with 242 training rows, a large grid would overfit the validation folds.

## Phase 5: Assess — and the tie nobody wants to admit

Here are the test-set numbers (61 patients), and they are the reason this article exists:

- **Logistic Regression:** ROC-AUC 0.960, accuracy 0.853, F1 0.853, recall 0.929
- **Random Forest:** ROC-AUC 0.961, accuracy 0.918, F1 0.915, recall 0.964
- **HistGradientBoosting:** ROC-AUC 0.963, accuracy 0.918, F1 0.915, recall 0.964

HistGradientBoosting "wins" on ROC-AUC by 0.002. On a test set of 61 patients, one patient is worth roughly 0.016 of AUC — so a 0.002 gap is noise, not a victory. Worse, the ranking flips if you look at cross-validation instead: on the 5-fold CV, Logistic Regression is best at 0.9037, ahead of the Random Forest's 0.8918. And the Random Forest and HistGradientBoosting make literally identical test errors: both miss exactly one case out of 28 and raise four false alarms out of 33 healthy patients.

So there is no winner. There is a statistical tie, and the honest report says so. I recommended the tuned Random Forest as the deployment candidate — joint-best accuracy, precision, recall and F1, AUC within noise of the leader, and direct feature importances that gradient boosting does not offer — with HistGradientBoosting as the designated challenger and Logistic Regression as the interpretable fallback. But "deployment" here means a research prototype with a clinician in the loop, never an automated decision.

The feature importances backed up the exploration: the thallium result (0.150), number of vessels (0.125), asymptomatic chest pain (0.107), max heart rate (0.097), and ST depression (0.085) dominate. Calibration looked sensible — patients the model scored under 0.2 were diseased 0% of the time; those scored over 0.8 were diseased 92% of the time — but the middle bins held two to five patients each, so that is indicative, not proven.

I also checked fairness by subgroup, because Assess demands it. Recall was 1.00 for women (n=20) and 0.95 for men (n=41); the oldest group (66–77) had only six test patients. Nothing looks disadvantaged beyond noise — and that is precisely the problem. Six patients cannot prove fairness. The check is reported because it was run, not because it settles anything.

## What SEMMA did not cover

SEMMA ends at Assess, so the monitoring plan — re-validate on a different hospital and a modern cohort, track input drift, log subgroup recall, retire the model once modern multi-site data exists — is mine, not the methodology's. SEMMA also never asked whether the problem was worth solving or what a false negative costs a patient. Those are business-understanding questions, and they belong to CRISP-DM. Used alone, SEMMA is a superb modelling discipline and an incomplete project discipline. Used with its eyes open, it forces exactly the habits that matter: sample honestly, explore before modelling, modify without leaking, model more than one way, and assess like someone will check your work — including when the assessment says "it's a tie."

## The disclaimer that matters more than the metrics

This is a teaching demonstration, not a diagnostic tool. The data are from one clinic in the 1980s. The sample is 303 patients. The models are classroom baselines. No number in this article should be used to judge any real person's heart. What the project *can* teach is the discipline: five phases, executed in order, with every number traceable to executed code and every limitation stated where it belongs — at the top, not in a footnote.

*The full executed notebook, report, and data dictionary are in the project repository. All metrics in this article match the executed notebook output exactly; the code, figures, and model comparison table are included there.*
