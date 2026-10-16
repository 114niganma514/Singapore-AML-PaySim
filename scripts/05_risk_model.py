import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
import pickle
import warnings

warnings.filterwarnings("ignore")


def main():
    # Load feature‑engineered dataset
    feature_data_path = "../test_data/featured_paysim.csv"
    try:
        df = pd.read_csv(feature_data_path)
    except Exception as e:
        print(f"Failed to load feature dataset: {str(e)}")
        return

    # Read feature name list from file
    feature_list_path = "../docs/feature_list.txt"
    try:
        with open(feature_list_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Failed to load feature list file: {str(e)}")
        return

    feature_cols = [line.strip() for line in lines[2:] if line.strip()]

    X = df[feature_cols].fillna(0)
    y = df["isFraud"]

    # Stratified train‑test split to preserve label distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set samples: {X_train.shape[0]}, fraud ratio: {round(y_train.mean() * 100, 4)}%")
    print(f"Test set samples: {X_test.shape[0]}, fraud ratio: {round(y_test.mean() * 100, 4)}%")

    # ========== Model 1: Logistic Regression Baseline (class‑weight for imbalance) ==========
    print("\n[Training Logistic Regression Baseline Model]")
    lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    lr.fit(X_train, y_train)
    lr_train_acc = accuracy_score(y_train, lr.predict(X_train))
    lr_test_acc = accuracy_score(y_test, lr.predict(X_test))
    print(f"Train accuracy: {round(lr_train_acc, 4)}")
    print(f"Test accuracy: {round(lr_test_acc, 4)}")

    # ========== Model 2: Random Forest (tree‑based model for imbalanced data) ==========
    print("\n[Training Random Forest Model]")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_train_acc = accuracy_score(y_train, rf.predict(X_train))
    rf_test_acc = accuracy_score(y_test, rf.predict(X_test))
    print(f"Train accuracy: {round(rf_train_acc, 4)}")
    print(f"Test accuracy: {round(rf_test_acc, 4)}")

    # Top‑10 feature importance
    feature_importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": rf.feature_importances_
    }).sort_values("importance", ascending=False).head(10)
    print("\nRandom Forest Top‑10 Important Features:")
    print(feature_importance.to_string(index=False))

    # Persist trained models and test dataset for evaluation script
    os.makedirs("../model", exist_ok=True)
    with open("../model/lr_model.pkl", "wb") as f:
        pickle.dump(lr, f)
    with open("../model/rf_model.pkl", "wb") as f:
        pickle.dump(rf, f)

    # Export held‑out test set
    test_data = pd.concat([X_test.reset_index(drop=True), y_test.reset_index(drop=True)], axis=1)
    test_data.to_csv("../test_data/test_set.csv", index=False)

    # Export top‑10 feature importance
    feature_importance.to_csv("../docs/feature_importance_top10.csv", index=False)

    print("\nModel training completed. Model files saved under model/ directory.")


if __name__ == "__main__":
    main()
