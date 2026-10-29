# We Lost 1 in 4 Customers. Here's What the Data Said — and What We Did About It

## The hook

One in four customers left. Not gradually, not quietly — 1,869 out of 7,043, a 26.5% churn rate. And the ones who left were the ones paying the most: $74.44 a month on average, against $61.27 for the customers who stayed. A telecom company losing its highest-paying customers at that rate doesn't have a marketing problem. It has a "we don't know who is about to leave, or why" problem.

That is the problem I set out to solve — and I did it by the book. Literally: I followed CRISP-DM, the Cross-Industry Standard Process for Data Mining, all six phases, in order, with no shortcuts. This is the story of that project: what the methodology forced me to do, what the data actually said, and what surprised me.

## Why CRISP-DM, and why it matters

Most data science projects fail in the same boring way: someone builds a model before anyone agrees what problem it solves, or what "good" looks like. CRISP-DM exists to prevent exactly that. Its six phases — Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment — form a loop, not a waterfall. You are expected to go backwards. And the methodology's most underrated rule is that deployment is a phase, not an afterthought: a model nobody can run is a hobby, not a deliverable.

So before I touched a single algorithm, I wrote down the success criteria: ROC-AUC of at least 0.80 on data the model had never seen, and recall of at least 0.70 on churners — because missing a customer who is about to leave costs far more than bothering one who isn't.

## The dataset

The IBM Telco Customer Churn sample: 7,043 customers, 21 columns. Demographics (gender, senior-citizen status, partner, dependents), account details (tenure, contract type, payment method, monthly and total charges), and services (phone, internet type, online security, tech support, streaming). One row per customer. The target is simple: did they churn, yes or no?

## Phase 1–2: The business question, then the data

The business question was deliberately narrow: which customers will churn, so retention can intervene *before* they leave? Not "understand churn in general" — predict it, in time to act.

Then the data started talking, and it had strong opinions. Month-to-month customers churn at 42.7%. Customers on two-year contracts? 2.8%. That single contrast is almost the whole story in one number: commitment is the best churn repellent this company has, and it isn't close. Electronic-check payers churn at 45.3%, while automatic payments sit around 15–17%. Fibre-optic customers churn at 41.9% versus 19.0% for DSL. Senior citizens churn at 41.7% versus 23.6% for everyone else. And churners are new: median tenure of 10 months, against 38 months for customers who stay.

The data also had exactly one real defect, and finding it is the kind of thing Phase 2 exists for. Pandas reported zero missing values — but `TotalCharges` was stored as text, and 11 rows contained a blank string instead of a number. All 11 were customers with zero months of tenure: brand-new customers with no charges yet. No rows were dropped, no customers were invented. The fix — coerce to numeric, fill those 11 with zero — came later, in preparation, with the reasoning written down.

## Phase 3: Preparation, the unglamorous 80%

Data preparation is where most of the actual work lives, and it was here too: drop the customer ID (an identifier, not a predictor), one-hot encode the 15 categorical features, scale the numbers only for the model that needs scaling, and split the data 80/20 with stratification so the test set has exactly the same 26.54% churn rate as the whole dataset. That test set was then locked away — touched once, at the very end.

One deliberate choice: no SMOTE, no synthetic churners. At 26.5%, the minority class isn't rare enough to justify inventing data, and `class_weight='balanced'` did the job cleanly.

## Phase 4–5: Three models, one surprise

I trained three models: Logistic Regression (the interpretable baseline), a Random Forest tuned by grid search (300 trees, max depth 10, best cross-validated ROC-AUC 0.8457), and HistGradientBoosting. All three cleared the 0.80 bar on the held-out test set. And then the surprise: **the simplest model won**. Logistic Regression scored ROC-AUC 0.8416, ahead of the tuned Random Forest (0.8388) and HistGradientBoosting (0.8362). The fancy models were better at accuracy and F1 by a hair, but on the metric we'd agreed in advance — ROC-AUC — the plain, explainable model took it. In a business setting, that's the best possible outcome: the model you can explain to a retention manager is also the model that performs best.

The numbers that matter for the business: the model catches 78.3% of churners (recall), and its top risk decile churns at 75.7% — nearly three times the base rate (2.85× lift). If you can only afford to call one in ten customers, call those.

What drives churn? Tenure first, then contract type, then total charges and monthly charges. The logistic coefficients tell the same story in plain language: long tenure and a two-year contract pull hard toward staying; fibre-optic service and a month-to-month contract pull toward leaving.

And the money: from the best model's actual test predictions — 293 churners correctly flagged, 81 missed — assuming $65 a month in average revenue, a 12-month horizon, and that a retention offer saves 20% of the customers we flag, scoring the full customer base would retain roughly 293 customers and about $228,540 of revenue per scoring cycle. The 20% save rate is an assumption, stated openly, not a measurement. It needs a real pilot to confirm. But even at half that save rate, the case for acting is obvious.

## Phase 6: Deployment, monitoring, and the ethics check

A model that lives in a notebook helps no one, so the project ends with a deployment plan, not a victory lap: a saved scoring pipeline, monthly batch scoring of every active customer, and a monitoring regime — alert if ROC-AUC drops below 0.75, investigate if the Population Stability Index on tenure, charges, or contract mix exceeds 0.2, retrain at least quarterly.

There is also an ethics section, and it is not decorative. Senior citizens churn at nearly double the rate of other customers, and the model uses senior-citizen status as an input. So the rules are explicit: the score is used only to *offer* retention help, never to deny service or raise prices, and false-positive and false-negative rates by senior-citizen status and gender get audited at every retrain. If a group starts getting systematically over-flagged, the sensitive feature comes out. I checked what I could check and refused to claim fairness I hadn't tested.

## What surprised me

Three things. First, that the simplest model won — I'd have bet on the Random Forest. Second, how much of the answer was visible before any modelling at all: the contract table alone (42.7% vs 2.8%) tells a retention team most of what it needs to know. Third, how much CRISP-DM's discipline mattered: fixing the success criteria before modelling meant the "best model" decision was already made when the numbers arrived. No moving goalposts, no cherry-picking.

## Conclusion

Churn prediction isn't a modelling problem. It's a business problem with a modelling step in the middle, and CRISP-DM kept it that way: question first, data second, preparation third, models fourth, honest evaluation fifth, and a deployment plan last. The result is a model that clears its bar, a scoring pipeline a team can actually run, and a retention list ordered by risk — with the top 10% of customers nearly three times as likely to leave as the average customer. That's not a notebook. That's a decision, waiting to be made every month.

*The full project — executed Colab notebook, detailed report, data dictionary, and saved model — is in the project repository (01-crisp-dm-telco-churn). The dataset is the public IBM Telco Customer Churn sample; all metrics are from a held-out test set of 1,409 customers, seed 42.*
