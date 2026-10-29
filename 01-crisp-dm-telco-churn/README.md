# CRISP-DM — Telco Customer Churn

Full CRISP-DM project (all 6 phases) predicting customer churn on the IBM Telco Customer Churn dataset (7,043 customers). Part of the CMPE 256 Data Mining Methodologies assignment — this folder is the CRISP-DM project; SEMMA and KDD projects live in sibling folders (`02-semma-...`, `03-kdd-...`).

## Results (held-out test set, n = 1,409, seed 42)

| Model | ROC-AUC | Accuracy | Precision (churn) | Recall (churn) | F1 (churn) |
|---|---|---|---|---|---|
| **Logistic Regression** | **0.8416** | 0.7381 | 0.5043 | 0.7834 | 0.6136 |
| Random Forest (tuned) | 0.8388 | 0.7523 | 0.5229 | 0.7647 | 0.6211 |
| HistGradientBoosting | 0.8362 | 0.7544 | 0.5263 | 0.7487 | 0.6181 |

Best model: **Logistic Regression (ROC-AUC 0.8416)** — clears the pre-agreed bar of ≥ 0.80; recall 0.7834 clears ≥ 0.70. Top risk decile churns at 75.71% (2.85× lift). Business impact (stated assumptions: $65/mo, 12-mo horizon, 20% save rate): ~293 customers and ~$228,540 revenue retained per scoring cycle on the full base.

## Open in Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pranith27/data-mining-methodologies/blob/main/01-crisp-dm-telco-churn/CRISP_DM_Telco_Churn.ipynb)

> The notebook's first code cell installs dependencies and the second downloads the dataset from its public URL, so it runs top-to-bottom in Colab with no local files.

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook CRISP_DM_Telco_Churn.ipynb
# or execute non-interactively:
jupyter nbconvert --to notebook --execute --inplace CRISP_DM_Telco_Churn.ipynb
```

The notebook uses `data/Telco-Customer-Churn.csv` if present, otherwise downloads it from https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv. No hard-coded local paths; seed 42 everywhere.

Note: if you execute locally with matplotlib 3.6.3, use `matplotlib-inline==0.1.6` (0.2.2 is incompatible with that matplotlib version in some environments).

## Files

- `CRISP_DM_Telco_Churn.ipynb` — executed Colab-ready notebook, all 6 CRISP-DM phases (23 cells, 14 code, 0 errors)
- `report.md` — detailed phase-by-phase report with real numbers from the executed notebook
- `medium-article.md` — Medium-ready article draft (~1,500 words)
- `critic-revisions.md` — critic log: world-renowned-CRISP-DM-authority persona, 3 revision rounds with scores
- `video-script.md` — 6-minute YouTube walkthrough script with timestamps
- `data/Telco-Customer-Churn.csv` — dataset (7,043 rows)
- `data/DATA_DICTIONARY.md` — column definitions and the known data-quality defect
- `artifacts/best_model.pkl` — saved best model (Logistic Regression pipeline)
- `artifacts/chart_churn_by_contract.png` — churn rate by contract chart
- `requirements.txt` — Python dependencies
