# Singapore AML Fraud Detection & Risk Compliance Analysis (PaySim)

End-to-end AML / fraud detection and compliance analysis pipeline on the **PaySim** synthetic
mobile-money dataset (6,362,620 transactions, 0.13% fraud), benchmarked against Singapore
**MAS Notice 626 / PDPA / FSMA**.

## Key results (held-out test set, 1.27M transactions)

| Model / operating point | AUC | PR-AUC | Precision | Recall | F1 |
|---|---|---|---|---|---|
| Random Forest (t=0.5) | - | - | 0.025 | 0.907 | 0.049 |
| XGBoost (t=0.5) | 0.982 | 0.615 | 0.035 | 0.892 | 0.068 |
| XGBoost, best-F1 threshold (t=0.98) | | | 0.513 | 0.615 | **0.559** |
| XGBoost, high-recall screening point (t=0.17) | | | 0.009 | 0.951 | 0.019 |

- Threshold tuning lifts XGBoost F1 from 0.068 to 0.559
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

## Data & how to run

Data is **not** included (raw ~470MB, intermediates >1GB; GitHub limit is 100MB/file).

1. Download PaySim from Kaggle (`ealaxi/paysim1`) and save the CSV as `test_data/paysim_raw.csv`
   (or save it as `test_data/Synthetic_Financial_datasets_log.csv` and run `python 00_convert_csv.py` from inside `test_data/`).
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scripts **from inside `scripts/`** (they use `../` relative paths), in order:

```bash
cd scripts
python 01_profile_paysim.py
python 02_clean_paysim.py
# ... through
python 09_xgb_hyperparam.py
```

`05_risk_model.py` regenerates `model/rf_model.pkl` (45MB, not committed), which `07`/`08` need.

## Tech stack
Python, pandas, NumPy, scikit-learn, XGBoost, Matplotlib
