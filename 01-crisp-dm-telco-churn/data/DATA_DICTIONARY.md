# Data Dictionary — Telco Customer Churn (IBM sample)

**Source:** https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
**Rows:** 7,043 customers (one row per customer) · **Columns:** 21 · **Target:** `Churn`
**Churn rate:** 26.54% (1,869 Yes / 5,174 No) · **Duplicates:** 0 rows, 0 duplicate `customerID`s
**Known defect:** `TotalCharges` is stored as text; 11 rows contain a blank string `' '` (all have `tenure == 0`). Coerced to numeric and filled with 0 in Phase 3 (new customers with no charges yet). No other missing values.

## Columns

| Column | Type (raw) | Values / range | Meaning |
|---|---|---|---|
| customerID | text | unique ID per customer | Identifier — dropped before modelling |
| gender | text | Male / Female | Customer gender |
| SeniorCitizen | int | 0 / 1 | 1 = senior citizen (16.2% of customers) |
| Partner | text | Yes / No | Has a partner |
| Dependents | text | Yes / No | Has dependents |
| tenure | int | 0–72 months | Months with the company (mean 32.4, median 29) |
| PhoneService | text | Yes / No | Has phone service |
| MultipleLines | text | Yes / No / No phone service | Multiple phone lines |
| InternetService | text | DSL / Fiber optic / No | Type of internet service |
| OnlineSecurity | text | Yes / No / No internet service | Online security add-on |
| OnlineBackup | text | Yes / No / No internet service | Online backup add-on |
| DeviceProtection | text | Yes / No / No internet service | Device protection add-on |
| TechSupport | text | Yes / No / No internet service | Tech support add-on |
| StreamingTV | text | Yes / No / No internet service | Streaming TV add-on |
| StreamingMovies | text | Yes / No / No internet service | Streaming movies add-on |
| Contract | text | Month-to-month / One year / Two year | Contract type |
| PaperlessBilling | text | Yes / No | Paperless billing enabled |
| PaymentMethod | text | Electronic check / Mailed check / Bank transfer (automatic) / Credit card (automatic) | How the customer pays |
| MonthlyCharges | float | $18.25–$118.75 | Monthly bill (mean $64.76) |
| TotalCharges | text → float | $18.80–$8,684.80 (after coercion) | Total amount billed to date |
| Churn | text | Yes / No | **Target:** customer left the company |

## Derived in the notebook

- `Churn_bin`: 1 if `Churn == 'Yes'`, else 0.
- `TotalCharges` (numeric): `pd.to_numeric(errors='coerce')`, blanks filled with 0.
- Features used for modelling: all columns except `customerID` and `Churn` (19 features: 15 categorical one-hot encoded, 4 numeric).
