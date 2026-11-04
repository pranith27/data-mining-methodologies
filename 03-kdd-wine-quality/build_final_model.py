"""Build the KDD deployment artifact: tuned Random Forest regressor, refit on all
1,359 unique wines — exactly the final model from KDD_Wine_Quality.ipynb cell 29.

Mirrors the notebook exactly:
- data/winequality-red.csv (sep=';'), drop exact duplicates, seed 42
- add_features: total_acidity, sulphur_ratio, alcohol_x_va
- preprocessor: log1p on skewed features, passthrough on the rest
- RandomForestRegressor(n_estimators=500, max_depth=10, min_samples_leaf=5,
                        random_state=42)  <- grid.best_params_ from the notebook
Sanity check: the same pipeline fit on the notebook's train split must reproduce
the executed test R2 of 0.4298 / RMSE of 0.6373 before the artifact is saved.
"""
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

RANDOM_STATE = 42
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "data", "winequality-red.csv")
SKEWED = ["residual sugar", "chlorides", "sulphates",
          "free sulfur dioxide", "total sulfur dioxide"]


def add_features(X):
    X = X.copy()
    X["total_acidity"] = X["fixed acidity"] + X["volatile acidity"] + X["citric acid"]
    X["sulphur_ratio"] = X["free sulfur dioxide"] / X["total sulfur dioxide"]
    X["alcohol_x_va"] = X["alcohol"] * X["volatile acidity"]
    return X


def load_clean():
    df = pd.read_csv(DATA_PATH, sep=";")
    df = df.drop_duplicates().reset_index(drop=True)
    X = add_features(df.drop(columns=["quality"]))
    return X, df["quality"], (df["quality"] >= 7).astype(int)


def make_preprocessor(X):
    passthrough = [c for c in X.columns if c not in SKEWED]
    return ColumnTransformer([
        ("log", FunctionTransformer(np.log1p, validate=False), SKEWED),
        ("pass", "passthrough", passthrough),
    ])


def make_pipeline(preprocessor):
    return Pipeline([
        ("pre", preprocessor),
        ("m", RandomForestRegressor(n_estimators=500, max_depth=10,
                                   min_samples_leaf=5,
                                   random_state=RANDOM_STATE, n_jobs=-1)),
    ])


def main():
    X, y_reg, y_clf = load_clean()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_reg, test_size=0.20, random_state=RANDOM_STATE, stratify=y_clf)

    # Sanity check against the executed notebook (test R2 = 0.4298, RMSE = 0.6373)
    check = make_pipeline(make_preprocessor(X_train)).fit(X_train, y_train)
    pred = check.predict(X_test)
    r2 = r2_score(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    print(f"Train-split reproduction: R2={r2:.4f} (notebook 0.4298), "
          f"RMSE={rmse:.4f} (notebook 0.6373)")
    assert abs(r2 - 0.4298) < 0.005 and abs(rmse - 0.6373) < 0.005, \
        "reproduction diverged from notebook!"

    # Deployment artifact: refit on ALL labelled wines (notebook cell 29)
    final_model = make_pipeline(make_preprocessor(X)).fit(X, y_reg)
    print(f"Final model refit on all {len(X)} wines with tuned hyperparameters.")

    artifacts = os.path.join(HERE, "artifacts")
    os.makedirs(artifacts, exist_ok=True)
    with open(os.path.join(artifacts, "best_model.pkl"), "wb") as f:
        pickle.dump(final_model, f)
    with open(os.path.join(artifacts, "MODEL_CARD.txt"), "w") as f:
        f.write(
            "KDD Wine Quality — deployment artifact\n"
            "Model: RandomForestRegressor(n_estimators=500, max_depth=10,\n"
            "       min_samples_leaf=5, random_state=42) in a sklearn Pipeline\n"
            "       with log1p on skewed features (see below), passthrough else.\n"
            "Training data: all 1,359 unique red wines (deduplicated),\n"
            "       UCI Wine Quality (Vinho Verde reds, Cortez et al. 2009).\n"
            "Engineered features (computed inside predict path): total_acidity\n"
            "       = fixed+volatile+citric acidity; sulphur_ratio =\n"
            "       free/total sulfur dioxide; alcohol_x_va = alcohol *\n"
            "       volatile acidity. log1p applied to: residual sugar,\n"
            "       chlorides, sulphates, free/total sulfur dioxide.\n"
            "Held-out test metrics of these hyperparameters: R2 = 0.4298,\n"
            "       RMSE = 0.6373 (ranking/QC use, not a taster replacement).\n"
            "Usage: pickle.load(open('best_model.pkl','rb')).predict(df)\n"
            "       where df has the 11 raw lab columns; build the 3 engineered\n"
            "       features first (see build_final_model.py: add_features).\n")
    print("Saved artifacts/best_model.pkl + MODEL_CARD.txt")


if __name__ == "__main__":
    main()
