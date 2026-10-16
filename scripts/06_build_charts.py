import matplotlib
matplotlib.use("Agg")  # Headless backend: save chart files without requiring a GUI/Tk
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
import numpy as np

warnings.filterwarnings("ignore")

# Global plotting configuration for English display, avoid garbled characters
plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150


def main():
    os.makedirs("../charts", exist_ok=True)
    input_path = "../test_data/cleaned_paysim.csv"
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Failed to load cleaned dataset: {str(e)}")
        return

    fraud = df[df["isFraud"] == 1]
    normal = df[df["isFraud"] == 0]

    # ========== Chart 1: Fraud proportion pie chart ==========
    plt.figure(figsize=(6, 6))
    sizes = [len(normal), len(fraud)]
    labels = ["Normal Transaction", "Fraud Transaction"]
    colors = ["#66b3ff", "#ff6b6b"]
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.3f%%", startangle=90)
    plt.title("Fraud Transaction Proportion")
    plt.tight_layout()
    plt.savefig("../charts/1_fraud_proportion.png", bbox_inches="tight")
    plt.close()
    print("Generated Chart 1: Fraud proportion pie chart")

    # ========== Chart 2: Fraud count by transaction type bar chart ==========
    plt.figure(figsize=(8, 5))
    fraud_by_type = fraud["type"].value_counts().sort_values(ascending=False)
    plt.bar(fraud_by_type.index, fraud_by_type.values, color="#ff6b6b")
    plt.title("Fraud Count by Transaction Type")
    plt.ylabel("Fraud Transaction Count")
    plt.xlabel("Transaction Type")
    plt.tight_layout()
    plt.savefig("../charts/2_fraud_by_type.png", bbox_inches="tight")
    plt.close()
    print("Generated Chart 2: Fraud distribution by transaction type")

    # ========== Chart 3: Normal vs Fraud amount box‑plot ==========
    plt.figure(figsize=(7, 5))
    # Log transform to compress long‑tail distribution for visualization
    data = [np.log1p(normal["amount"]), np.log1p(fraud["amount"])]
    plt.boxplot(data, patch_artist=True,
                boxprops=dict(facecolor="#66b3ff", alpha=0.7))
    plt.xticks([1, 2], ["Normal", "Fraud"])
    plt.title("Transaction Amount Distribution (Log Scale)")
    plt.ylabel("Log(Amount)")
    plt.tight_layout()
    plt.savefig("../charts/3_amount_boxplot.png", bbox_inches="tight")
    plt.close()
    print("Generated Chart 3: Amount distribution box‑plot")

    # ========== Chart 4: 24‑hour fraud transaction volume trend ==========
    plt.figure(figsize=(10, 4))
    hour_trend = fraud["hour_of_day"].value_counts().sort_index()
    plt.plot(hour_trend.index, hour_trend.values, marker="o", color="#ff6b6b", linewidth=2)
    plt.title("Fraud Transaction Count by Hour of Day")
    plt.xlabel("Hour (0‑23)")
    plt.ylabel("Fraud Transaction Count")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("../charts/4_fraud_hour_trend.png", bbox_inches="tight")
    plt.close()
    print("Generated Chart 4: Hourly fraud trend chart")

    print("\nAll visualization charts generated and saved under charts/ directory")


if __name__ == "__main__":
    main()
