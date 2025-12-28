import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import pdfplumber

PLOT_DIR = os.path.join("static", "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


# -----------------------------
# LOAD DATASET
# -----------------------------
def load_dataset(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        return pd.read_csv(path)

    if ext == ".pdf":
        tables = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.extend(table)

        return pd.DataFrame(tables[1:], columns=tables[0])


# -----------------------------
# DATA QUALITY INDEX
# -----------------------------
def calculate_dqi(df):
    missing_rate = df.isnull().mean().mean()
    duplicate_rate = df.duplicated().mean()
    return round(100 - (missing_rate + duplicate_rate) * 100, 2)


# -----------------------------
# CLEANING PIPELINE
# -----------------------------
def clean_dataset(path):
    df = load_dataset(path)
    df_before = df.copy()

    # DQI before
    dqi_before = calculate_dqi(df)

    # -----------------------------
    # REMOVE DUPLICATES
    # -----------------------------
    df = df.drop_duplicates()

    # -----------------------------
    # DATA TYPE CONSISTENCY
    # -----------------------------
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().mean() > 0.5:
            df[col] = converted

    # -----------------------------
    # CATEGORICAL NORMALIZATION
    # -----------------------------
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({"nan": np.nan})
        )

    # -----------------------------
    # HANDLE MISSING VALUES
    # -----------------------------
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("unknown")

    # -----------------------------
    # INVALID VALUE CORRECTION
    # -----------------------------
    for col in df.select_dtypes(include=["int64", "float64"]).columns:
        if (df[col] < 0).any():
            df.loc[df[col] < 0, col] = df[col].median()

    # -----------------------------
    # OUTLIER HANDLING (CAPPING)
    # -----------------------------
    for col in df.select_dtypes(include=["int64", "float64"]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df[col] = np.clip(df[col], lower, upper)

    # -----------------------------
    # DQI after
    # -----------------------------
    dqi_after = calculate_dqi(df)

    # -----------------------------
    # VISUAL ANALYTICS
    # -----------------------------
    plots = []
    for col in df.select_dtypes(include=["int64", "float64"]).columns:
        plt.figure()
        df[col].hist()
        plt.title(f"{col} Distribution")
        plt.tight_layout()

        fname = col.replace(" ", "_") + ".png"
        plt.savefig(os.path.join(PLOT_DIR, fname))
        plt.close()

        plots.append(f"plots/{fname}")

    # -----------------------------
    # NLG SUMMARY
    # -----------------------------
    nlg_summary = (
        f"The dataset initially had a quality score of {dqi_before}%. "
        f"After automatically resolving missing values, duplicates, "
        f"categorical inconsistencies, invalid values, and outliers, "
        f"the Dataset Quality Index improved to {dqi_after}%. "
        f"The dataset is now structurally and statistically reliable."
    )

    return df, dqi_before, dqi_after, plots, nlg_summary
