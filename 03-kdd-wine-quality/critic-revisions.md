# Critic Revision Log — KDD Wine Quality Project

## The critic persona prompt

Every revision round below was conducted under this critic prompt:

> "You are a world-renowned authority on KDD / knowledge discovery in databases, author of award-winning books on data mining methodology, a keynote speaker who has taught the Fayyad et al. (1996) KDD process for decades. Review this KDD project the way you would review a submission to a top venue: brutally honest, no politeness, no grade inflation. Score each section out of 10, name every weakness precisely — methodological errors, unjustified decisions, numbers that do not match the code output, missing steps, overclaims — and say exactly what must change. A score of 10 means publishable as-is; anything below 8 means revise before anyone sees it."

The critic reviewed the notebook, the report, the article and the supporting files against the executed notebook output. Each round lists the issues found, the fix applied, and the re-score. Nothing in this log is invented: every issue below was a real defect found in the draft and fixed in the delivered files.

---

## Round 1 — "Your numbers don't match your own output"

**Scope reviewed:** First executed notebook (31 cells) + draft report claims.
**Critic's verdict:** The methodology is sound, but the write-up quotes numbers from an earlier prototype run, not from the executed notebook. That is the cardinal sin in a KDD report: the interpretation step must describe what the mining step actually produced.

| # | Issue | Fix |
|---|---|---|
| 1.1 | Report/notebook claimed feature engineering added "+0.004 R²". The executed notebook says +0.0089 (R² 0.4191 → 0.4280). | Corrected to +0.009 everywhere (notebook conclusion, report §4.4 and §5.5, article). |
| 1.2 | Notebook claimed the Random Forest classifier was "balanced at 54% precision / 54% recall". The executed notebook says precision 0.5455, recall 0.4865 — 55% / 49%, F1 0.5143. The 54/54 figures came from the prototype run, whose classifier differed. | Corrected to 55% precision / 49% recall (F1 0.51) in notebook, report and article. |
| 1.3 | The sulphates row in the "known vs new" table said "confirmed with importance 0.04–0.25 depending on method" — mixing a correlation (r = +0.25) with an importance (0.04) as if they were the same quantity. | Rewritten as "Pearson r = +0.25, Random Forest importance 0.04". |
| 1.4 | First code cell `!pip install` failed under PEP 668 (externally-managed environment) when executed outside Colab, leaving an error block in the delivered notebook. | Changed to `import sys` + `!{sys.executable} -m pip install ...`, which installs into the active interpreter in both Colab and a local venv. Notebook re-executed clean. |
| 1.5 | Tuned Random Forest hyperparameters differed between prototype (max_depth 20, test R² 0.4308) and executed notebook (max_depth 10, test R² 0.4298) — near-tie in grid search, flipped by parallel fold evaluation. | Report states the executed notebook's values (max_depth 10, CV R² 0.3874, test R² 0.4298) and notes the tuning gain is negligible (0.4280 → 0.4298). The notebook was executed twice end-to-end; both runs produced identical metrics. |

**Scores after Round 1:** Selection 9/10, Preprocessing 9/10, Transformation 8/10, Data Mining 8/10, Interpretation 7/10 → **8/10** (held back by the mismatched numbers), Deployment 8/10.

---

## Round 2 — "Show your working, and stop hiding the weak spots"

**Scope reviewed:** Revised notebook + report draft.
**Critic's verdict:** The numbers now match, but three methodological points are glossed over, and one analysis in the prototype was flat-out wrong.

| # | Issue | Fix |
|---|---|---|
| 2.1 | The prototype's error-by-score analysis accidentally used the *classifier's* predictions instead of the regressor's, producing nonsense residuals (mean residual ≈ the quality score itself). | Rebuilt in the notebook as Step 5d using the tuned regressor's predictions; verified output (mean residual −0.012, MAE by score 0.36–1.66, regression-to-the-mean pattern) and wrote it up in report §5.4. |
| 2.2 | Dropping 240 duplicates (15% of the data) was stated without a leakage argument. A reviewer will ask why you threw away a seventh of the data. | Added the explicit justification in notebook Step 2 and report §2.2: identical rows can straddle the train/test split and leak; verified the target distribution barely moved after dedup (high-quality share 13.57% → 13.54%). |
| 2.3 | The sulphates sign flip — correlation +0.25 but linear coefficient −0.08 once other variables are controlled — was left unexplained, which looks like an error. | Added to report §5.2: a single coefficient is not a causal effect; the flip is reported and explained, not hidden. |
| 2.4 | Classification was presented without justifying why accuracy was not the headline metric. | Added the explicit note in report §4.3: predicting "not premium" for everything scores ~86% accuracy and learns nothing; F1 and ROC-AUC are the honest metrics under an 86/14 split. |
| 2.5 | Deployment was prose only — no artefact a winery could actually run. | Added Step 6 code cell: the tuned model refit on all 1,359 wines, a `predict_quality()` function, and two illustrative profiles (good profile 6.89 premium-likely; faulty profile 4.56 not premium). |

**Scores after Round 2:** Selection 9/10, Preprocessing 9/10, Transformation 8/10, Data Mining 8/10, Interpretation 9/10, Deployment 8/10.

---

## Round 3 — "Final pass: is every claim traceable, and are the limits honest?"

**Scope reviewed:** Final notebook (re-executed), report.md, medium-article.md, README.md, data dictionary.
**Critic's verdict:** The work is now defensible. Remaining nits are about traceability and honesty of limits, not correctness.

| # | Issue | Fix |
|---|---|---|
| 3.1 | Medium article draft needed a word-count check against the 1,300–1,800 target and a number audit. | Counted: 1,785 words, in range. Every figure in the article (R² 0.43, RMSE 0.64, AUC 0.89–0.90, F1 0.51, +0.009 engineering gain, 89.3% within ±1 point) re-checked against executed notebook output. |
| 3.2 | The claim "no Medium URL" / "no fake links" needed enforcing: the article must not invent a publication link. | Article ends with a source note only, no URL. README states the GitHub username placeholder must be replaced by the user. |
| 3.3 | Limitations section read as boilerplate. A KDD interpretation step must name the specific ways this knowledge fails. | Expanded report §6.3 with five concrete limits: subjective target, single region/style, correlation ≠ causation (with the alcohol example), rare scores poorly modelled (n=10 at score 3, n=18 at score 8), engineered features adding almost nothing. |
| 3.4 | Reproducibility claim ("executed clean") needed evidence, not assertion. | Verified and recorded: notebook executed twice end-to-end with identical metrics; 31 cells, 21 code cells, execution counts 1–21 sequential, 0 errors, 5 figures embedded. Stated in report and README. |
| 3.5 | The notebook's Step 5 text said the model "explains R² ≈ 0.43" while the tuned value is 0.4298 and untuned 0.4280 — fine — but the conclusion also needed the residual ceiling stated the same way everywhere. | Standardised on "R² ≈ 0.43, ~57% of variance unexplained" across notebook, report and article. |

**Final scores after Round 3:**

| Section | Score /10 |
|---|---|
| Step 1 — Selection | 9 |
| Step 2 — Preprocessing | 9 |
| Step 3 — Transformation | 8 |
| Step 4 — Data Mining | 8 |
| Step 5 — Interpretation / Evaluation | 9 |
| Deployment / Knowledge Use | 8 |
| Reproducibility & reporting | 9 |
| **Overall** | **8.6 / 10** |

**Critic's closing note:** "The project is honest about a modest R² instead of hiding behind a tuned metric, and the interpretation step does real work — the binned driver analysis and the error-by-score table are the strongest parts. The two points it loses are structural: the dataset is small and single-region, so no amount of methodology can make the findings general, and the tuning step is deliberately light, which is correct but leaves the modelling section thinner than the interpretation section. Ship it."
