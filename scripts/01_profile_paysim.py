import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")


def main():
    # Create output directory automatically
    os.makedirs("../docs", exist_ok=True)

    # Load raw dataset
    file_path = "../test_data/paysim_raw.csv"
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Failed to load dataset: {str(e)}")
        return

    # Print profiling results to console
    print("=" * 60)
    print("[1] Basic Dataset Information")
    print(f"Total rows: {df.shape[0]}  |  Total columns: {df.shape[1]}")
    mem_mb = round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2)
    print(f"Memory usage: {mem_mb} MB")

    print("\n[2] Column Names and Data Types")
    print(df.dtypes)

    print("\n[3] Missing Value Statistics")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("No missing values")

    print("\n[4] Label Distribution (Fraud / Normal)")
    label_dist = df["isFraud"].value_counts()
    print(label_dist)
    fraud_ratio = round(label_dist[1] / df.shape[0] * 100, 4)
    print(f"Fraud sample ratio: {fraud_ratio} %")

    print("\n[5] Transaction Type Distribution")
    type_dist = df["type"].value_counts()
    print(type_dist)

    print("\n[6] Fraud Count per Transaction Type")
    fraud_by_type = df.groupby("type")["isFraud"].sum().sort_values(ascending=False)
    print(fraud_by_type)

    print("\n[7] Descriptive Statistics for Amount Field")
    print(df["amount"].describe().apply(lambda x: format(x, ".2f")))

    # Save profiling report to file
    report_path = "../docs/data_profile_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("PaySim Mobile Financial Fraud Dataset Data Profiling Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Total rows: {df.shape[0]}  |  Total columns: {df.shape[1]}\n")
        f.write(f"Fraud sample ratio: {fraud_ratio} %\n\n")
        f.write("Fraud count by transaction type:\n")
        f.write(fraud_by_type.to_string())

    print("\nData profiling completed. Report saved to docs/data_profile_report.txt")


if __name__ == "__main__":
    main()
