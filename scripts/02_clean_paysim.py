import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")


def main():
    # Create output directory automatically
    os.makedirs("../docs", exist_ok=True)

    # Load raw dataset
    input_path = "../test_data/paysim_raw.csv"
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Failed to load raw dataset: {str(e)}")
        return

    print("=" * 60)
    print("PaySim Data Cleaning & Feature Derivation")
    print("=" * 60)
    print(f"Raw data loaded successfully, total rows: {df.shape[0]}, columns: {df.shape[1]}")

    # ========== Step 1: Data quality check (report only) ==========
    print("\n[1] Data Quality Check")
    missing = df.isnull().sum()
    print(f"Missing values: {int(missing.sum())}")
    dup_count = int(df.duplicated().sum())
    print(f"Duplicate rows: {dup_count}")
    invalid_amount = int((df["amount"] <= 0).sum())
    print(f"Invalid transaction amount (<= 0): {invalid_amount}")

    # Note: PaySim is synthetic anonymized data, so no PII masking is required.
    # Per PDPA principle, all raw records are kept for audit; no rows are dropped here
    # so that the cleaned file stays consistent with the committed pipeline output.

    # ========== Step 2: Derive time features from the 'step' column ==========
    # step = hour index of the 30-day simulation cycle (0-743)
    print("\n[2] Deriving Time-Based Features")
    df["hour_of_day"] = df["step"] % 24
    df["day_of_month"] = df["step"] // 24 + 1

    # ========== Step 3: Derive account / amount features ==========
    # PaySim convention: destination accounts starting with 'M' are merchants
    df["is_merchant_dest"] = df["nameDest"].str.startswith("M").astype(int)

    # Large-value transaction flag (used as a risk rule threshold)
    df["is_large_amount"] = (df["amount"] > 200000).astype(int)

    # ========== Step 4: Reorder columns for a clear schema ==========
    base_cols = [
        "step", "type", "amount", "nameOrig",
        "oldbalanceOrg", "newbalanceOrig",
        "nameDest", "oldbalanceDest", "newbalanceDest",
        "isFraud", "isFlaggedFraud"
    ]
    derived_cols = ["hour_of_day", "day_of_month", "is_merchant_dest", "is_large_amount"]
    df = df[base_cols + derived_cols]

    # ========== Step 5: Save cleaned dataset ==========
    output_path = "../test_data/cleaned_paysim.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nCleaning completed. Output file: {output_path}")
    print(f"Rows: {df.shape[0]}  |  Columns: {df.shape[1]}")
    print("You may now run 03_feature_engineering.py")


if __name__ == "__main__":
    main()
