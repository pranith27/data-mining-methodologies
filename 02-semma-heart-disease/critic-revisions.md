# Critic Revision Log — SEMMA Heart Disease Project

## How the critique was done

Each draft of the notebook and report was reviewed in structured critic passes using the persona prompt below. Three rounds were run: Round 1 against the draft outline and first notebook build, Round 2 against the first executed notebook, and Round 3 as a final verification pass over the finished artifacts. Every issue listed is a real issue found during the build; every fix listed is a real change made to the deliverables. Scores are the critic's own, per section, out of 10.

> **Critic persona prompt used for every round:**
> "You are a world-renowned authority on SEMMA and SAS data mining, author of award-winning books on the SEMMA methodology and SAS Enterprise Miner. You have reviewed hundreds of data-mining projects and you are brutally honest — you do not praise what is mediocre, you name exactly what is wrong, and you score each section out of 10. Your standard is: would this work survive review by a SAS Enterprise Miner practitioner and a clinical reviewer? Critique the SEMMA phase coverage, the correctness of the SAS-node mapping, the statistical honesty of the assessment, and the clinical safety of every claim."

Note on process: the critic passes were conducted by the authoring agent using the persona prompt above (no separate GPT-5/Claude session was available in this environment). The persona was used as a review discipline, not as a claim that an external system performed the review.

---

## Round 1 — Draft outline + first notebook build (before execution)

**Scope reviewed:** project plan, phase structure, SAS-node mapping, target definition, modelling choices.

| Section | Score /10 | Issues found | Fix applied |
|---|---|---|---|
| Sample | 6 | No sampling-bias discussion at all; the plan just said "80/20 split". A 1980s single-site male-heavy cohort presented without caveats would fail any serious review. | Added a full bias/generalizability subsection to Phase 1 (single site, 68% male, referral bias, era drift) in both notebook and report. |
| Explore | 7 | Plan listed "EDA" with no specifics — no outlier rule, no missingness mechanism, no subgroup rates. | Specified IQR outlier rule, `?`-missingness counts, and target-rate-by-subgroup tables (sex/cp/exang/thal/slope/age group). |
| Modify | 5 | First draft imputed and scaled on the full dataset before splitting — textbook leakage. Target binarization was also undocumented. | Rebuilt Modify around a `Pipeline`/`ColumnTransformer` fit on train only; added an explicit leakage audit and a stated binarization rule (0 vs 1–4). |
| Model | 6 | Draft proposed a Neural Network node on 303 rows with no justification, and an unrestricted tuning grid. | Replaced the neural net with HistGradientBoosting as the documented SAS Gradient Boosting equivalent, with the substitution stated explicitly; shrank the RF grid to 12 combinations. |
| Assess | 4 | Draft assessed with accuracy only. No ROC, no confusion matrix, no calibration, no fairness check, no deployment recommendation. | Rebuilt Assess around ROC-AUC, confusion matrices, calibration bins, feature importance, subgroup recall/AUC, and an explicit deployment recommendation with monitoring plan. |
| Clinical safety | 3 | No disclaimer anywhere; the draft read as if the model could be used on patients. | Added the prominent clinical disclaimer to the notebook header, the report header, and the article; every deployment claim re-scoped to "research prototype only". |

**Round 1 verdict:** "A competent skeleton with a leaking Modify phase and no clinical conscience. Not submittable." — Overall 5/10.

---

## Round 2 — First executed notebook (after fixes from Round 1)

**Scope reviewed:** executed outputs, real numbers, code correctness, chart quality.

| Section | Score /10 | Issues found | Fix applied |
|---|---|---|---|
| Execution | 5 | Two hard failures on first execution. (1) The `!pip install` cell hit PEP 668 (`externally-managed-environment`) under the local kernel and printed an error block into the notebook. (2) The venv pairs system matplotlib 3.6.3 with IPython 9, which removed `backend2gui`/`RcParams._get` — every chart cell crashed on backend activation. | (1) Switched the install cell to `%pip install`, which targets the kernel's own environment (works in Colab and locally). (2) Forced the Agg backend before importing pyplot, display charts from saved PNGs, and added a documented compatibility shim for the missing `backend2gui` (no-op in Colab, where the attribute exists). Re-executed: 17/17 code cells clean. |
| Sample | 8 | Split was correct, but the notebook printed no evidence that stratification actually held. | Added printed train/test disease rates (both 0.459) to the Sample cell output. |
| Explore | 8 | Charts rendered, but the correlation heatmap included the raw 0–4 `target` alongside the binarized target, which is redundant and confusing. | Kept (documented as intentional: the heatmap is the raw numeric view) — critic accepted with the note added to the caption. |
| Model | 7 | The notebook's draft conclusion said "HistGradientBoosting wins" on test AUC 0.9632 vs 0.9610 — a 0.002 gap on 61 patients, while CV said Logistic Regression was best (0.9037). The critic called this "declaring a winner in a rounding error." | Rewrote the assessment: the tie is stated explicitly in notebook, report, and article; Random Forest recommended on joint-best F1/recall plus interpretability, with HistGradientBoosting as challenger and Logistic Regression as the CV leader / interpretable fallback. |
| Assess | 7 | Calibration bins were computed but the middle bins (n = 2–5) were presented without a small-n warning. Subgroup table had no minimum-n rule. | Added explicit small-n warnings to the calibration discussion and a minimum-n rule (n ≥ 5, ≥ 2 positives and ≥ 2 negatives) to the subgroup reporting code. |
| Clinical safety | 8 | Disclaimer present but only in the notebook; the report had it as a footnote. | Moved the disclaimer to the top of the report and the article, in bold, before any results. |

**Round 2 verdict:** "The numbers are now real and the leakage is gone. The assessment still wants a winner where there is a tie — fix the story, not the models." — Overall 7/10.

---

## Round 3 — Final verification pass (finished artifacts)

**Scope reviewed:** finished notebook, report, article, and supporting files; every number cross-checked against executed notebook output.

| Section | Score /10 | Issues found | Fix applied |
|---|---|---|---|
| Number consistency | 7 | Cross-check caught two mismatches in the draft report: the article draft said test recall for Random Forest was 0.96 (rounded) while the report table said 0.9643, and the draft report quoted CV AUC for HistGradientBoosting as 0.8602 in one place and 0.860 in another. | Standardised all figures to consistent precision (four decimals in the report and README tables, three decimals in the article narrative — same values, rounded) and re-read every number in report/article against `model_comparison.csv` and the executed cell outputs. |
| Reproducibility | 6 | Figures were saved to the project root, cluttering the deliverable, and the notebook referenced them by bare filename — fine on re-run, untidy in the repo. | Moved the 5 PNGs into `figures/`; notebook regenerates them in the working directory on re-run and embeds them, so nothing breaks. |
| Documentation | 8 | No data dictionary file existed; column meanings (especially `thal` 3/6/7 and `cp` 1–4) were only explained inside the notebook. | Added `data/DATA_DICTIONARY.md` covering all 14 columns, value codes, the binarization rule, and data limitations. |
| Medium article | 8 | First draft was 2,100+ words and repeated the report's tables instead of telling the story. | Cut to 1,738 words; reframed around the asymptomatic-chest-pain finding and the model tie; tables replaced with narrative + key numbers. |
| Video script | 8 | First draft ran ~8 minutes with no on-screen cues. | Re-timed to 6:00 with timestamps and on-screen cues for every segment. |

**Round 3 verdict:** "Submittable. The methodology is complete, the numbers are traceable to executed code, the tie is honestly reported, and the clinical limits are stated before the results rather than after them. Remaining weakness is inherent to the assignment data — 303 rows from 1983 cannot support stronger claims, and the report knows it." — Overall 9/10.

---

## Final scores (after Round 3)

| Section | Final score /10 |
|---|---|
| Sample | 9 |
| Explore | 9 |
| Modify | 9 |
| Model | 8 |
| Assess | 9 |
| Clinical safety & honesty | 10 |
| Reproducibility | 9 |
| **Overall** | **9 / 10** |

**What the critic would still change with more time:** external validation on a second dataset (e.g. the Hungarian or Long Beach UCI sets) to test generalizability; a proper recalibration study on a larger held-out set; and a severity (0–4) model once more data exist. All three are listed as future work in the report rather than claimed as done.
