# Data Mining Methodologies — CRISP-DM, SEMMA & KDD

**Author:** Pranith Varma Pakalapati
**Course:** CMPE 256, San José State University
**Assignment:** Data Mining Process Assignment — principled, phase-by-phase data science with three methodologies, a different dataset for each, all artifacts in GitHub


## What this repo is

Three complete, self-contained data mining projects. Each one follows its methodology from start to finish — business problem, data, preparation, modelling, evaluation, and deployment — and each one has an executed notebook, so every number in the reports comes from code that actually ran. No placeholder results.

## The three projects

| # | Methodology | Dataset | Size | Task | Headline test result |
|---|---|---|---|---|---|
| 1 | **CRISP-DM** — 6 phases | Telco Customer Churn (IBM sample) | 7,043 rows × 21 columns | Predict which customers churn | Logistic Regression: ROC-AUC **0.8416**, top-decile lift **2.85×** |
| 2 | **SEMMA** — 5 phases | UCI Heart Disease, Cleveland | 303 rows × 14 columns | Predict heart disease | HistGradientBoosting: ROC-AUC **0.9632**; Random Forest: F1 **0.9153** |
| 3 | **KDD** — 5 steps | UCI Wine Quality, Red | 1,599 rows × 12 columns (1,359 after removing duplicates) | Predict wine quality score | Tuned Random Forest: R² **0.4298**, RMSE **0.6373** |

Key findings in one line each:

- **Churn:** month-to-month customers churn at 42.7%, versus 2.8% on two-year contracts. Tenure is the strongest protective factor.
- **Heart disease:** chest-pain type, exercise-induced angina, and thalassemia dominate the models — but this is a small, single-site, 1980s sample, so it is a teaching prototype, not a diagnostic tool.
- **Wine quality:** higher alcohol (correlation +0.48) and lower volatile acidity (−0.39) go with higher quality; residual sugar is unrelated (+0.01). Even the best model explains only about 43% of quality — sensory scores are noisy.

## What's inside

```
data-mining-methodologies/
├── README.md                  ← this file: results, how to run, how to push to GitHub
├── index.html                 ← the submission website (opens as the GitHub Pages homepage)
├── SUBMISSION_CHECKLIST.md    ← tick-box checklist for the final steps before Nov 3
├── 01-crisp-dm-telco-churn/
├── 02-semma-heart-disease/
└── 03-kdd-wine-quality/
```

Every project folder contains the same set of deliverables:

```
<project>/
├── <Notebook>.ipynb       Colab-ready notebook, already executed (outputs saved)
├── report.md              Detailed phase-by-phase report with real numbers
├── critic-revisions.md    3 critic rounds, persona prompt quoted, fixes documented
├── artifacts/             Saved final deployment model (best_model.pkl) + MODEL_CARD.txt
├── build_final_model.py   Reproducible script that trains and saves the artifact
├── README.md              Project-specific notes and Colab link
├── requirements.txt       Python packages needed (pinned versions)
├── data/                  The dataset + DATA_DICTIONARY.md
└── figures/               Charts used in the report and video (SEMMA, KDD)
```

Notebook sizes, verified Oct 28, 2026: CRISP-DM 23 cells, SEMMA 24 cells, KDD 31 cells — **0 error cells in any notebook**.

## How to run a notebook

### Option A — Google Colab (easiest, no install)

1. Open the notebook from the project folder on GitHub.
2. Click **Open in Colab** (the badge at the top of the project's README).
3. **Runtime → Run all.** Cell 1 installs the packages; cell 2 downloads the dataset from its public URL. Every number reproduces. Seed is 42 throughout.

### Option B — On your own computer

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r 01-crisp-dm-telco-churn/requirements.txt
jupyter nbconvert --to notebook --execute --inplace 01-crisp-dm-telco-churn/CRISP_DM_Telco_Churn.ipynb
```

Swap in the other notebook paths for the SEMMA and KDD projects. Each notebook also works from its own `data/` file if you run it offline.

## How to push this to GitHub — step by step

### Step 1 — Repository (already created)

https://github.com/pranith27/data-mining-methodologies — public, currently empty. The steps below push this folder into it.

### Step 2 — Push this folder

Open a terminal **inside the unzipped `data-mining-methodologies` folder** and run:

```bash
git init
git add .
git commit -m "CMPE 256: CRISP-DM, SEMMA and KDD projects"
git branch -M main
git remote add origin https://github.com/pranith27/data-mining-methodologies.git
git push -u origin main
```

If Git asks you to sign in, sign in with your GitHub account (use a personal access token as the password if GitHub asks for one).

### Step 3 — Colab links (already done)

The Colab badges in the three project READMEs already point at pranith27/data-mining-methodologies on `main` — no placeholder step is needed.
### Step 4 — Turn on GitHub Pages (this creates your website URL)

1. On GitHub, open your repo → **Settings** → **Pages**.
2. Under "Build and deployment", Source: **Deploy from a branch**.
3. Branch: **main**, folder: **/ (root)**. Click **Save**.
4. Wait a minute, refresh the Pages settings page — it will show your site address:

```
https://pranith27.github.io/data-mining-methodologies/
```

5. Open that URL and click each project link once to confirm the notebooks, reports, and articles load.

### Step 5 — Submit the website URL in Canvas

Paste this URL as your Canvas submission, before **Nov 3, 2026, 23:59 PT**:

```
https://pranith27.github.io/data-mining-methodologies/
```

## Deployment artifacts

Every project ships a saved final model plus a model card, so the "deployment" phase is a runnable artifact, not just a notebook cell:

- `01-crisp-dm-telco-churn/artifacts/best_model.pkl` — Logistic Regression churn pipeline (ROC-AUC 0.8416)
- `02-semma-heart-disease/artifacts/best_model.pkl` — tuned Random Forest pipeline (test ROC-AUC 0.961)
- `03-kdd-wine-quality/artifacts/best_model.pkl` — tuned Random Forest regressor pipeline (test R² 0.4298)

Each `artifacts/` folder also has a `MODEL_CARD.txt` (what the model is, what data it trained on, how to load and call it). The `build_final_model.py` script in each project reproduces the artifact from the raw data and sanity-checks the metrics against the executed notebook before saving. Built with scikit-learn==1.9.1 (see pinned `requirements.txt`).

## Honest limitations (stated in the deliverables, not hidden)

- **Critic revisions:** each project went through 3 critic rounds using the assignment's pumped-up persona prompt ("world-renowned authority … author of award-winning books"), quoted in each `critic-revisions.md`. Those rounds were run in this workspace — no separate GPT-5/Claude session was available here.
- **SEMMA without SAS:** SEMMA comes from SAS Enterprise Miner and no SAS licence was available, so it is implemented in Python. The SEMMA report maps every step to its SAS node (Sample → Data Partition, Explore → StatExplore, and so on). The methodology logic is the same; the vendor tool is not.
- **Heart disease sample:** only 303 patients, 61 in the test set. The AUC looks strong, but uncertainty is wide — treat it as a prototype, never as medical advice.
- **Wine quality:** R² of 0.43 means most of what makes a wine taste good is not in the lab measurements. The model finds patterns; it does not give a recipe for better wine.

## Published articles and video walkthroughs

All three Medium articles are published, and all three narrated walkthrough videos are on YouTube:

**Medium articles**
- CRISP-DM (Telco Churn) — [We Lost 1 in 4 Customers. Here's What the Data Said — and What We Did About It](https://medium.com/@pranithvarma.234/we-lost-1-in-4-customers-heres-what-the-data-said-and-what-we-did-about-it-440560d129bb)
- SEMMA (Heart Disease) — [I Ran a 1980s Heart Dataset Through SEMMA — and the Models Tied](https://medium.com/@pranithvarma.234/i-ran-a-1980s-heart-dataset-through-semma-and-the-models-tied-259cc51eb0dd)
- KDD (Wine Quality) — [What 1,599 Wines Taught Me About Quality — A KDD Story](https://medium.com/@pranithvarma.234/what-1-599-wines-taught-me-about-quality-a-kdd-story-3b7e54325f24)

**YouTube walkthroughs** (narrated, male voiceover)
- CRISP-DM — https://youtu.be/A_KGWct-lUg
- SEMMA — https://youtu.be/srAwSKYl9YM
- KDD — https://youtu.be/fTEAhjRz0nE

## Sources

- Telco churn: IBM sample dataset, github.com/IBM/telco-customer-churn-on-icp4d
- Heart disease: UCI Machine Learning Repository, Cleveland processed set
- Wine quality: UCI Machine Learning Repository, Cortez et al. (2009)
- CRISP-DM: Chapman et al. (2000). SEMMA: SAS Institute. KDD: Fayyad, Piatetsky-Shapiro & Smyth (1996).
