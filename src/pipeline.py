import pandas as pd
import pdfplumber
import os
import matplotlib.pyplot as plt

PLOT_DIR = os.path.join("static", "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

def load_dataset(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        return pd.read_csv(file_path)

    elif ext == ".pdf":
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.extend(table)

        if not tables:
            raise ValueError("No tabular data found in PDF")

        return pd.DataFrame(tables[1:], columns=tables[0])

    else:
        raise ValueError("Unsupported file format")

def calculate_dqi(df):
    missing_rate = df.isnull().mean().mean()
    duplicate_rate = df.duplicated().mean()
    return round(100 - (missing_rate * 100 + duplicate_rate * 100), 2)

def generate_nlg_summary(df_before, df_after, dqi_before, dqi_after):
    text = []
    text.append(
        f"The uploaded dataset contained {df_before.shape[0]} records and {df_before.shape[1]} attributes."
    )

    missing = df_before.isnull().sum().sum()
    if missing > 0:
        text.append(
            f"{missing} missing values were detected and resolved using adaptive imputation strategies."
        )

    duplicates = df_before.duplicated().sum()
    if duplicates > 0:
        text.append(
            f"{duplicates} duplicate records were identified and removed."
        )

    text.append(
        f"The Dataset Quality Index improved from {dqi_before}% to {dqi_after}% after preprocessing."
    )

    text.append(
        "The cleaned dataset is consistent and ready for further analytics or machine learning tasks."
    )

    return " ".join(text)

def clean_dataset(file_path):
    df = load_dataset(file_path)
    df_before = df.copy()

    dqi_before = calculate_dqi(df)

    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().mean() > 0.5:
            df[col] = converted

    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("Unknown")

    dqi_after = calculate_dqi(df)

    plots = []
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    for col in numeric_cols:
        safe_col = col.replace(" ", "_")

        plt.figure()
        df[col].hist()
        plt.title(f"{col} Distribution")
        plt.tight_layout()

        filename = f"{safe_col}_hist.png"
        plt.savefig(os.path.join(PLOT_DIR, filename))
        plt.close()

        plots.append(f"plots/{filename}")

    nlg_summary = generate_nlg_summary(df_before, df, dqi_before, dqi_after)

    return df, dqi_before, dqi_after, plots, nlg_summary
