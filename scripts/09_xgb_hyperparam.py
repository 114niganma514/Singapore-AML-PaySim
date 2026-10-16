# -*- coding: utf-8 -*-
"""XGBoost hyperparameter tuning (fast): grid search on a subsample, then final
training on the full training set; evaluate on the held-out test set."""
import pandas as pd
import numpy as np
import pickle
import os
import warnings
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score
import xgboost as xgb

warnings.filterwarnings("ignore")
plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150

base = r"D:\Singapore_AML_RiskCompliance_PaySim"
t0 = time.time()

# ---------- 1. Load data & reproduce the same split as 05/08 ----------
print("Loading feature data...")
df = pd.read_csv(os.path.join(base, "test_data", "featured_paysim.csv"))
with open(os.path.join(base, "docs", "feature_list.txt"), "r", encoding="utf-8") as f:
    lines = f.readlines()
feature_cols = [line.strip() for line in lines[2:] if line.strip()]
X = df[feature_cols].fillna(0)
y = df["isFraud"]
del df
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
del X, y
print(f"Train {X_train.shape[0]}, Test {X_test.shape[0]}  ({time.time()-t0:.0f}s)")

scale_pos_weight = int(np.sum(y_train == 0) / np.sum(y_train == 1))

# ---------- 2. Fast grid search on a stratified subsample ----------
sub_frac = 0.15  # ~760k rows for search speed
X_sub, _, y_sub, _ = train_test_split(X_train, y_train, test_size=1 - sub_frac, random_state=7, stratify=y_train)
X_sub_tr, X_sub_va, y_sub_tr, y_sub_va = train_test_split(
    X_sub, y_sub, test_size=0.25, random_state=7, stratify=y_sub
)
print(f"Search: train {X_sub_tr.shape[0]}, val {X_sub_va.shape[0]}  ({time.time()-t0:.0f}s)")

grid = []
for depth in [5, 7]:
    for lr in [0.05, 0.1]:
        for est in [150, 250]:
            grid.append({"max_depth": depth, "learning_rate": lr, "n_estimators": est})

results = []
for i, p in enumerate(grid):
    st = time.time()
    model = xgb.XGBClassifier(
        n_estimators=p["n_estimators"], max_depth=p["max_depth"],
        learning_rate=p["learning_rate"], subsample=0.9, colsample_bytree=0.9,
        scale_pos_weight=scale_pos_weight, eval_metric="auc",
        n_jobs=-1, random_state=42, tree_method="hist",
    )
    model.fit(X_sub_tr, y_sub_tr, verbose=False)
    va_prob = model.predict_proba(X_sub_va)[:, 1]
    auc = roc_auc_score(y_sub_va, va_prob)
    results.append((auc, p))
    print(f"  [{i+1}/{len(grid)}] depth={p['max_depth']} lr={p['learning_rate']} "
          f"est={p['n_estimators']} -> valAUC={auc:.4f} ({time.time()-st:.0f}s)")

results.sort(key=lambda r: -r[0])
best_auc, best_p = results[0]
print(f"Best params: {best_p} (valAUC={best_auc:.4f})")

# ---------- 3. Final training on full training set ----------
print("Training final XGBoost on full train set...")
final = xgb.XGBClassifier(
    n_estimators=best_p["n_estimators"], max_depth=best_p["max_depth"],
    learning_rate=best_p["learning_rate"], subsample=0.9, colsample_bytree=0.9,
    scale_pos_weight=scale_pos_weight, eval_metric="auc",
    n_jobs=-1, random_state=42, tree_method="hist",
)
final.fit(X_train, y_train, verbose=False)
print(f"Final training done ({time.time()-t0:.0f}s)")

# ---------- 4. Evaluate on test set ----------
y_prob = final.predict_proba(X_test)[:, 1]
y_pred = final.predict(X_test)
metrics = {
    "precision": precision_score(y_test, y_pred),
    "recall": recall_score(y_test, y_pred),
    "f1": f1_score(y_test, y_pred),
    "auc": roc_auc_score(y_test, y_prob),
    "pr_auc": average_precision_score(y_test, y_prob),
}

# Threshold sweep for best-F1 / high-recall
thresholds = np.arange(0.01, 0.99, 0.01)
precs, recs, f1s = [], [], []
for t in thresholds:
    yp = (y_prob >= t).astype(int)
    precs.append(precision_score(y_test, yp, zero_division=0))
    recs.append(recall_score(y_test, yp))
    f1s.append(f1_score(y_test, yp, zero_division=0))
precs, recs, f1s = np.array(precs), np.array(recs), np.array(f1s)
best_idx = int(np.argmax(f1s))
hr_mask = recs >= 0.95
hr_idx = np.where(hr_mask)[0][-1] if hr_mask.any() else 0

report = []
report.append("=" * 70)
report.append("XGBoost Hyperparameter Tuning Report (Step 09)")
report.append("=" * 70)
report.append(f"Search space: max_depth x learning_rate x n_estimators on {X_sub_tr.shape[0]:,} rows")
report.append(f"Best params: {best_p} (validation AUC = {round(best_auc, 4)})")
report.append("\nGrid search results (sorted by validation AUC):")
for auc, p in sorted(results, key=lambda r: -r[0]):
    report.append(f"  depth={p['max_depth']} lr={p['learning_rate']} est={p['n_estimators']} -> {round(auc,4)}")
report.append("\nFinal model on held-out test set:")
report.append(f"  Precision: {round(metrics['precision'],4)}")
report.append(f"  Recall:    {round(metrics['recall'],4)}")
report.append(f"  F1-Score:  {round(metrics['f1'],4)}")
report.append(f"  AUC:       {round(metrics['auc'],4)}")
report.append(f"  PR-AUC:    {round(metrics['pr_auc'],4)}")
report.append(f"  Default t=0.5: P={round(precs[np.where(thresholds==0.5)[0][0]],4)} "
              f"R={round(recs[np.where(thresholds==0.5)[0][0]],4)} F1={round(f1s[np.where(thresholds==0.5)[0][0]],4)}")
report.append(f"  Best-F1 threshold = {thresholds[best_idx]:.2f}: "
              f"P={round(precs[best_idx],4)} R={round(recs[best_idx],4)} F1={round(f1s[best_idx],4)}")
report.append(f"  High-recall threshold (R>=0.95) = {thresholds[hr_idx]:.2f}: "
              f"P={round(precs[hr_idx],4)} R={round(recs[hr_idx],4)} F1={round(f1s[hr_idx],4)}")
report.append("\nComparison with step-08 default XGBoost (depth6 lr0.1 est200):")
report.append("  Step-08 XGB: P=0.0352 R=0.8917 F1=0.0678 AUC=0.9817 PR-AUC=0.6151")
report.append(f"  Step-09 XGB: P={round(metrics['precision'],4)} R={round(metrics['recall'],4)} "
              f"F1={round(metrics['f1'],4)} AUC={round(metrics['auc'],4)} PR-AUC={round(metrics['pr_auc'],4)}")

with open(os.path.join(base, "docs", "xgb_tuning_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
for line in report:
    print(line)

# ---------- 5. Save tuned model + tuning curve ----------
with open(os.path.join(base, "model", "xgb_tuned_model.pkl"), "wb") as f:
    pickle.dump(final, f)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(thresholds, precs, label="Precision", color="#66b3ff")
ax.plot(thresholds, recs, label="Recall", color="#ff6b6b")
ax.plot(thresholds, f1s, label="F1-Score", color="#82ca9d")
ax.axvline(thresholds[best_idx], color="gray", ls="--", lw=1, alpha=0.7)
ax.axvline(thresholds[hr_idx], color="gray", ls=":", lw=1, alpha=0.7)
ax.set_title("Tuned XGBoost - Threshold Tuning (Dashed: best-F1, Dotted: R>=0.95)")
ax.set_xlabel("Classification Threshold"); ax.set_ylabel("Score")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
ax.legend(loc="center right", fontsize=9); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(base, "charts", "xgb_tuned_threshold.png"), bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: model/xgb_tuned_model.pkl, charts/xgb_tuned_threshold.png")
print(f"Total time: {time.time()-t0:.0f}s")
