---
name: risk-compliance-analysis
description: >
  End-to-end risk and compliance analysis for transactional datasets,
  including data profiling, cleaning & anonymization, risk feature engineering,
  multi-dimensional risk segmentation, regulatory compliance checks, visualization,
  metric validation, and auditable business insights reports.
  Designed to align with Singapore MAS AML/CFT requirements and FinTech compliance standards.
---

# Workflow

0.  **Raw Data Conversion** *(only if the original Kaggle file is present)*
    - Run `test_data/00_convert_csv.py` from the `test_data/` directory to convert
      `Synthetic_Financial_datasets_log.csv` into the standard `paysim_raw.csv`.
    - If `paysim_raw.csv` already exists, this step only verifies readability and can be skipped.

1.  **Initialization & Data Understanding**
    - Read the input dataset (transaction CSV/Excel) and the project references.
    - Align with `references/metric_definitions.md` and `references/analysis_dimensions.md` to confirm analysis scope, regulatory thresholds, and business rules.
    - Perform granularity and field validation.

2.  **Data Profiling & Quality Check**
    - Run `scripts/01_profile_paysim.py` to generate a full data quality report:
      - Field overview, row count, and schema validation.
      - Missing values, duplicates, and data type consistency.
      - Anomalous values (e.g., extreme transaction amounts, negative balances, invalid timestamps).
    - Output a structured data quality log for audit trail (`docs/data_profile_report.txt`).

3.  **Cleaning & Feature Derivation**
    - Run `scripts/02_clean_paysim.py`:
      - Check and report missing values, duplicates and invalid amounts.
      - Derive risk/time features: `hour_of_day`, `day_of_month`, `is_merchant_dest`, `is_large_amount`.
      - PaySim is synthetic anonymized data, so no PII masking is required (PDPA note).
    - Output the cleaned dataset `test_data/cleaned_paysim.csv` (all rows preserved for audit).

4.  **Risk Feature Engineering**
    - Run `scripts/03_feature_engineering.py`:
      - Derive core risk features (e.g., transaction frequency, velocity, amount deviation, risk tier labels).
      - Apply regulatory thresholds from `references/metric_definitions.md` (e.g., large cash transaction reporting limits).
      - Enrich with derived dimensions (time of day, transaction channel, customer segment).
    - Output `test_data/featured_paysim.csv` and the modelling feature list `docs/feature_list.txt`.

5.  **Fraud Pattern & Risk Analysis**
    - Run `scripts/04_fraud_pattern_analysis.py`:
      - Analyze by customer risk tier, transaction type, channel, amount bracket, and time period.
      - Identify high-risk patterns (e.g., structuring, rapid movement between accounts, unusual geographic activity).
      - Perform compliance checks against AML/CFT scenarios and output flagged cases (`docs/fraud_pattern_analysis.txt`).

6.  **Risk Modeling**
    - Run `scripts/05_risk_model.py`:
      - Train baseline (Logistic Regression) and tree-based (Random Forest) risk-control models on the imbalanced dataset.
      - Persist models to `model/` and export the held-out test set `test_data/test_set.csv`.

7.  **Visualization & Dashboard-ready Output**
    - Run `scripts/06_build_charts.py`:
      - Create charts aligned with the analysis dimensions: risk distribution, transaction trends, compliance violation breakdowns.
      - Ensure charts include proper titles, labels, and context for business users (`charts/*.png`).

8.  **Metric Validation & Model Evaluation**
    - Run `scripts/07_model_evaluation.py`:
      - Verify model metrics (precision / recall / F1 / AUC) against the hard-rule baseline.
      - Check for calculation errors, mismatched denominators, and inconsistent aggregation levels.
      - Validate flagged risk cases against business rules (`docs/model_evaluation_report.txt`).

9.  **Model Comparison & Threshold Tuning**
    - Run `scripts/08_model_tuning_xgb.py`:
      - Train XGBoost and compare against Logistic Regression / Random Forest (precision / recall / F1 / AUC / PR-AUC).
      - Sweep classification thresholds to find the best-F1 and high-recall (R>=0.95) operating points.
      - Output `docs/model_tuning_report.txt`, `charts/threshold_tuning.png` and `model/xgb_model.pkl`.

10. **XGBoost Hyperparameter Tuning**
    - Run `scripts/09_xgb_hyperparam.py`:
      - Grid search (max_depth / learning_rate / n_estimators) on a stratified subsample, then final training on the full set.
      - Evaluate the tuned model vs the step-08 default on the held-out test set.
      - Output `docs/xgb_tuning_report.txt`, `model/xgb_tuned_model.pkl`, `charts/xgb_tuned_threshold.png`.

11. **Final Report & Delivery**
    - Populate the report at `assets/Singapore AML & Risk Compliance Data Analysis Report.md` with:
      - Data overview and quality statement.
      - Methodology and assumptions.
      - Key risk findings and compliance observations.
      - Supporting charts and tables.
      - Recommendations, limitations, and audit trail.
    - Ensure all claims include supporting data references.
