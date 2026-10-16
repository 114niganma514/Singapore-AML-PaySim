# Singapore AML Fraud Detection & Risk Compliance Analysis (PaySim)

End-to-end AML / fraud detection and compliance analysis pipeline on the **PaySim** synthetic
mobile-money dataset (6,362,620 transactions, 0.13% fraud), benchmarked against Singapore
**MAS Notice 626 / PDPA / FSMA**.

## Key results (held-out test set)

| Model | AUC | PR-AUC | Recall | Notes |
|---|---|---|---|---|
| XGBoost (step 08) | 0.982 | 0.615 | 0.892 | best overall |
| Random Forest | - | - | 0.907 | highest recall at t=0.5 |
| XGBoost, best-F1 threshold (0.98) | | | 0.615 | F1 0.068 -> 0.559 |
| XGBoost, high-recall point (t=0.17) | | | 0.951 | operational screening point |

- 25 risk features; balance fields excluded to prevent leakage
- Risk grading of ~6.35M accounts: 8,213 high-risk; STR candidate triage
- Full numbers: `docs/model_tuning_report.txt`, `docs/xgb_tuning_report.txt`, `docs/report_metrics.json`

## Structure

```
scripts/      01_profile -> 02_clean -> 03_features -> 04_patterns -> 05_model
              -> 06_charts -> 07_evaluation -> 08_xgb_threshold_tuning -> 09_xgb_hyperparam
docs/         reports and metrics
charts/       figures
model/        LR / XGBoost models (Random Forest .pkl excluded, 45MB - regenerate with 05)
references/   MAS / PDPA / FSMA notes, KYC, glossary
assets/       compliance analysis report
test_data/    00_convert_csv.py (data files not committed)
```

## Data

Data is **not** included (raw ~470MB, intermediates >1GB; GitHub limit is 100MB/file).
Download PaySim from Kaggle (`ealaxi/paysim1`), save it as `test_data/paysim_raw.csv`,
then run the scripts in order. Note: `scripts/09_xgb_hyperparam.py` uses an absolute
base path (`D:\Singapore_AML_RiskCompliance_PaySim`) - change it to your local path.

## Tech stack
Python, pandas, NumPy, scikit-learn, XGBoost, Matplotlib
