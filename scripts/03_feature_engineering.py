import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")


def main():
    # Load cleaned dataset
    input_path = "../test_data/cleaned_paysim.csv"
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Failed to load cleaned dataset: {str(e)}")
        return

    print(f"Cleaned data loaded successfully, total rows: {df.shape[0]}")

    # ========== Category 1: Basic transaction features ==========
    # Log transformation to compress long‑tail distribution
    df["amount_log"] = np.log1p(df["amount"])

    # Amount binning: use cat.codes to obtain numeric encoding
    df["amount_level"] = pd.cut(
        df["amount"],
        bins=[0, 1000, 10000, 100000, float("inf")],
        labels=[1, 2, 3, 4]
    ).cat.codes

    # One‑hot encoding for transaction type
    type_dummies = pd.get_dummies(df["type"], prefix="type")
    df = pd.concat([df, type_dummies], axis=1)

    # ========== Category 2: Time‑based features ==========
    # Midnight transaction flag (0‑6 o'clock is low‑activity high‑risk period)
    df["is_midnight"] = ((df["hour_of_day"] >= 0) & (df["hour_of_day"] < 6)).astype(int)

    # Weekday / weekend flag (simulate 30‑day cycle, day 1 is Monday)
    df["weekday"] = (df["day_of_month"] - 1) % 7
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)

    # ========== Category 3: Origin‑account aggregated features ==========
    print("Calculating origin‑account aggregated features...")
    orig_agg = df.groupby("nameOrig").agg(
        orig_total_count=("amount", "count"),
        orig_total_amount=("amount", "sum"),
        orig_avg_amount=("amount", "mean"),
        orig_max_amount=("amount", "max"),
        orig_type_nunique=("type", "nunique")
    ).reset_index()

    df = df.merge(orig_agg, on="nameOrig", how="left")

    # ========== Category 4: Destination‑account aggregated features ==========
    print("Calculating destination‑account aggregated features...")
    dest_agg = df.groupby("nameDest").agg(
        dest_total_count=("amount", "count"),
        dest_total_amount=("amount", "sum"),
        dest_avg_amount=("amount", "mean")
    ).reset_index()

    df = df.merge(dest_agg, on="nameDest", how="left")

    # Fill nulls (new accounts have no historical data on first transaction)
    agg_cols = [col for col in df.columns if col.endswith(("_count", "_amount", "_nunique"))]
    df[agg_cols] = df[agg_cols].fillna(0)

    # ========== Define final modelling feature columns ==========
    # Strictly exclude balance fields (official note: fraud transaction balances are zeroed out, causing data leakage)
    exclude_cols = [
        "nameOrig", "nameDest", "type",
        "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest",
        "isFraud"
    ]
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    print(f"Final available modelling feature count: {len(feature_cols)}")

    # Save feature‑engineered dataset
    output_path = "../test_data/featured_paysim.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    # Save feature column list
    os.makedirs("../docs", exist_ok=True)
    with open("../docs/feature_list.txt", "w", encoding="utf-8") as f:
        f.write(f"List of Modelling Features (Total: {len(feature_cols)})\n")
        f.write("=" * 40 + "\n")
        for col in feature_cols:
            f.write(col + "\n")

    print(f"Feature engineering completed. Output file: {output_path}")


if __name__ == "__main__":
    main()
