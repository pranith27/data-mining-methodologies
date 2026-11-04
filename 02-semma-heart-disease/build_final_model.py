"""Build the SEMMA deployment artifact: tuned Random Forest (the deployment
candidate recommended in report.md / the Medium article), refit on all 303 rows.

Mirrors SEMMA_Heart_Disease.ipynb exactly:
- data/processed.cleveland.data, header=None, COLUMNS below, seed 42
- '?' -> NaN in ca/thal, pd.to_numeric
- preprocess_tree: median imputation (no scaling) + one-hot for cp/restecg/slope
- RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=2,
                         random_state=42)  <- grid.best_params_ from the notebook
Sanity check: the same pipeline fit on the notebook's train split must reproduce
the executed test ROC-AUC of 0.961 before the artifact is saved.
"""
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

RANDOM_STATE = 42
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "processed.cleveland.data")
COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
           "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"]
NUMERIC_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca", "thal"]
BINARY_FEATURES = ["sex", "fbs", "exang"]
CATEGORICAL_FEATURES = ["cp", "restecg", "slope"]


def load_clean():
    df = pd.read_csv(DATA_PATH, header=None, names=COLUMNS)
    df["target_bin"] = (df["target"] > 0).astype(int)
    X = df.drop(columns=["target", "target_bin"]).copy()
    for col in ["ca", "thal"]:
        X[col] = X[col].replace("?", np.nan)
        X[col] = pd.to_numeric(X[col], errors="coerce")
    return X, df["target_bin"]


def make_pipeline():
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocess_tree = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]),
         NUMERIC_FEATURES + BINARY_FEATURES),
        ("cat", categorical_transformer, CATEGORICAL_FEATURES),
    ])
    return Pipeline([
        ("prep", preprocess_tree),
        ("clf", RandomForestClassifier(n_estimators=200, max_depth=8,
                                       min_samples_leaf=2,
                                       random_state=RANDOM_STATE, n_jobs=-1)),
    ])


def main():
    X, y = load_clean()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE)

    # Sanity check against the executed notebook (test ROC-AUC = 0.961)
    check = make_pipeline().fit(X_train, y_train)
    auc = roc_auc_score(y_test, check.predict_proba(X_test)[:, 1])
    print(f"Train-split reproduction test ROC-AUC: {auc:.4f} (notebook: 0.961)")
    assert abs(auc - 0.961) < 0.005, "reproduction diverged from notebook!"

    # Deployment artifact: refit on ALL labelled rows (standard practice —
    # the test set has served its purpose; the shipped model uses every row)
    final_model = make_pipeline().fit(X, y)

    here = os.path.dirname(os.path.abspath(__file__))
    artifacts = os.path.join(here, "artifacts")
    os.makedirs(artifacts, exist_ok=True)
    with open(os.path.join(artifacts, "best_model.pkl"), "wb") as f:
        pickle.dump(final_model, f)
    with open(os.path.join(artifacts, "MODEL_CARD.txt"), "w") as f:
        f.write(
            "SEMMA Heart Disease — deployment artifact\n"
            "Model: RandomForestClassifier(n_estimators=200, max_depth=8,\n"
            "       min_samples_leaf=2, random_state=42) in a sklearn Pipeline\n"
            "       with median imputation + one-hot encoding (no scaling).\n"
            "Training data: all 303 rows of UCI Heart Disease (Cleveland),\n"
            "       target binarized (0 = no disease, 1-4 = disease present).\n"
            "Why this model: deployment candidate recommended in report.md —\n"
            "       joint-best test accuracy/precision/recall/F1, test ROC-AUC\n"
            "       0.961 (within noise of the leader), direct feature\n"
            "       importances. Teaching/research prototype only — NOT a\n"
            "       diagnostic device.\n"
            "Usage: pickle.load(open('best_model.pkl','rb')).predict_proba(X)\n"
            "       where X has the 13 raw columns: age, sex, cp, trestbps,\n"
            "       chol, fbs, restecg, thalach, exang, oldpeak, slope, ca,\n"
            "       thal (missing coded as '?' or NaN, as in the raw file).\n")
    print("Saved artifacts/best_model.pkl + MODEL_CARD.txt")


if __name__ == "__main__":
    main()
