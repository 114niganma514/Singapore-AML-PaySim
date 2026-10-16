import pandas as pd
import os


def main():
    # Original source file (Kaggle "Synthetic_Financial_datasets_log.csv", optional)
    raw_file = "../test_data/Synthetic_Financial_datasets_log.csv"
    # Standard output CSV used by subsequent pipeline scripts
    output_file = "../test_data/paysim_raw.csv"

    # Case 1: Original source exists -> convert to standard UTF-8 CSV
    if os.path.exists(raw_file):
        print("Original source found. Converting to standard CSV...")
        try:
            df = pd.read_csv(raw_file, sep=",", engine="python")
        except Exception as e:
            print(f"Failed to read source file: {str(e)}")
            return
        print(f"Read successfully: {len(df)} rows, {len(df.columns)} columns")
        print("Column list:", df.columns.tolist())
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"\nStandard CSV generated: {output_file}")
        print("You may now run 01_profile_paysim.py")
        return

    # Case 2: Standard raw dataset already exists -> verify it is ready for the pipeline
    if os.path.exists(output_file):
        print(f"Standard raw dataset already exists: {output_file}")
        print("No conversion needed. Verifying the dataset is readable...")
        try:
            df = pd.read_csv(output_file)
            print(f"Verified: {len(df)} rows, {len(df.columns)} columns")
            print("Column list:", df.columns.tolist())
            print("Raw dataset is ready. You may now run 01_profile_paysim.py")
        except Exception as e:
            print(f"Failed to read existing raw dataset: {str(e)}")
        return

    print(f"No source dataset found under test_data/")
    print(f"Expected file: {raw_file}")
    print(f"  or already-converted file: {output_file}")


if __name__ == "__main__":
    main()
