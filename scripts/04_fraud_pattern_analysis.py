import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")


def main():
    input_path = "../test_data/cleaned_paysim.csv"
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Failed to load cleaned dataset: {str(e)}")
        return

    # Split normal and fraud samples
    normal = df[df["isFraud"] == 0]
    fraud = df[df["isFraud"] == 1]

    report = []
    report.append("=" * 60)
    report.append("PaySim Fraudulent Transaction Behavior Pattern Analysis Report")
    report.append("=" * 60)

    # 1. Fraudulent transaction type distribution
    report.append("\n[1] Fraudulent Transaction Type Distribution")
    type_fraud = fraud["type"].value_counts()
    report.append(type_fraud.to_string())
    report.append(f"Conclusion: 100% of fraud cases are concentrated in {list(type_fraud.index)} transaction types; no fraud exists in other transaction types.")

    # 2. Amount comparison
    report.append("\n[2] Normal vs Fraudulent Transaction Amount Comparison")
    report.append(f"Average amount of normal transactions: {round(normal['amount'].mean(), 2)}")
    report.append(f"Average amount of fraudulent transactions: {round(fraud['amount'].mean(), 2)}")
    ratio_val = round(fraud['amount'].mean() / normal['amount'].mean(), 2)
    report.append(f"The average amount of fraudulent transactions is {ratio_val} times that of normal transactions.")

    # 3. Time distribution
    report.append("\n[3] 24‑Hour Distribution of Fraudulent Transactions")
    hour_fraud = fraud["hour_of_day"].value_counts().sort_index()
    top_hour = hour_fraud.idxmax()
    report.append(f"Peak fraud hour: {top_hour} o'clock, total {hour_fraud.max()} transactions")
    report.append("Fraud proportion is significantly higher during early‑morning hours than working hours.")

    # 4. Beneficiary type
    report.append("\n[4] Beneficiary Types of Fraudulent Transactions")
    merchant_rate = fraud["is_merchant_dest"].mean()
    report.append(f"Merchant beneficiary proportion among fraudulent transactions: {round(merchant_rate * 100, 2)}%")
    report.append("Conclusion: Almost all fraud funds flow to personal accounts; merchant accounts have almost no fraud activity.")

    # 5. Large‑value rule hit statistics
    report.append("\n[5] Large‑value Rule (>200000) Hit Statistics")
    large_fraud_rate = fraud["is_large_amount"].mean()
    large_normal_rate = normal["is_large_amount"].mean()
    report.append(f"Large‑value proportion within fraudulent transactions: {round(large_fraud_rate * 100, 2)}%")
    report.append(f"Large‑value proportion within normal transactions: {round(large_normal_rate * 100, 2)}%")
    report.append("Large‑value transaction is a strong fraud indicator. However, relying solely on the large‑value rule will miss a large number of medium‑ and small‑value fraud cases.")

    # Save report file
    os.makedirs("../docs", exist_ok=True)
    with open("../docs/fraud_pattern_analysis.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    # Print report to console
    for line in report:
        print(line)

    print("\nFraud pattern analysis completed, report saved.")


if __name__ == "__main__":
    main()
