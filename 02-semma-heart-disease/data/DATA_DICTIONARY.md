# Data Dictionary — UCI Heart Disease, Cleveland Processed Set

- **Source:** UCI Machine Learning Repository — https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data
- **File in this project:** `data/processed.cleveland.data` (303 rows, 14 columns, no header row, comma-separated)
- **Original creators:** Hungarian Institute of Cardiology (Budapest), University Hospital Zurich, University Hospital Basel, V.A. Medical Center Long Beach, and the Cleveland Clinic Foundation (Robert Detrano, M.D., Ph.D.). Cleveland set collected at the Cleveland Clinic, 1980s.
- **Note on missing values:** missing values are coded as `?` in the raw file (4 in `ca`, 2 in `thal`). There is no header row; column names below are the standard UCI names applied on load.

## Columns

| # | Column | Type | Meaning / values |
|---|---|---|---|
| 1 | `age` | numeric (years) | Age in years. Range in this set: 29–77, mean 54.4 |
| 2 | `sex` | binary | 0 = female, 1 = male. 97 female, 206 male |
| 3 | `cp` | categorical (1–4) | Chest-pain type: 1 = typical angina, 2 = atypical angina, 3 = non-anginal pain, 4 = asymptomatic |
| 4 | `trestbps` | numeric (mm Hg) | Resting blood pressure on admission. Range 94–200, mean 131.7 |
| 5 | `chol` | numeric (mg/dl) | Serum cholesterol. Range 126–564, mean 246.7 |
| 6 | `fbs` | binary | Fasting blood sugar > 120 mg/dl: 0 = false, 1 = true |
| 7 | `restecg` | categorical (0–2) | Resting electrocardiographic results: 0 = normal, 1 = ST-T wave abnormality, 2 = probable/definite left ventricular hypertrophy |
| 8 | `thalach` | numeric (bpm) | Maximum heart rate achieved during exercise stress test. Range 71–202, mean 149.6 |
| 9 | `exang` | binary | Exercise-induced angina: 0 = no, 1 = yes |
| 10 | `oldpeak` | numeric | ST depression induced by exercise relative to rest. Range 0–6.2, mean 1.04 |
| 11 | `slope` | categorical (1–3) | Slope of the peak-exercise ST segment: 1 = upsloping, 2 = flat, 3 = downsloping |
| 12 | `ca` | numeric (0–3, with `?`) | Number of major vessels (0–3) coloured by fluoroscopy. 4 values missing (`?`) |
| 13 | `thal` | categorical (3, 6, 7, with `?`) | Thalassemia / thallium stress-test result: 3 = normal, 6 = fixed defect, 7 = reversible defect. 2 values missing (`?`) |
| 14 | `target` | integer (0–4) | Diagnosis of heart disease: 0 = no disease (< 50% diameter narrowing), 1–4 = disease present with increasing severity. Counts: 0 → 164, 1 → 55, 2 → 36, 3 → 35, 4 → 13 |

## Target binarization (used for modelling)

The raw `target` (0–4) is **binarized to 0/1** for this project: 0 = no disease (164 patients), 1 = disease present, i.e. original values 1–4 (139 patients). Binarized disease prevalence = **45.87%**. The 5-level severity information is discarded deliberately — with only 303 rows, the severity classes (13 patients in class 4) are too small to model reliably, and the binary question ("disease present or not") is the standard formulation for this dataset in the literature.

## Known limitations of the data

- Single site (Cleveland Clinic), single era (1980s); 68% male; patients were referred for cardiac evaluation, so prevalence is far above the general population.
- Only 6 rows (2%) have any missing value, all in `ca`/`thal`.
- No patient identifiers, no dates, no outcome follow-up — this is a cross-sectional diagnostic dataset, not a prognosis dataset.
