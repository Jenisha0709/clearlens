import pandas as pd
import pdfplumber
import matplotlib
matplotlib.use("Agg")  # IMPORTANT: no GUI backend
import matplotlib.pyplot as plt
import os

PLOT_DIR = os.path.join("static", "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


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


def calculate_dqi(df):
    missing_rate = df.isnull().mean().mean()
    duplicate_rate = df.duplicated().mean()
    return round(100 - (missing_rate + duplicate_rate) * 100, 2)


def clean_dataset(path):
    df = load_dataset(path)
    df_before = df.copy()

    # DQI before
    dqi_before = calculate_dqi(df)

    # Convert numeric-like columns safely
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().mean() > 0.5:
            df[col] = converted

    # Remove duplicates
    df = df.drop_duplicates()

    # Handle missing values (NO inplace=True)
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("Unknown")

    # DQI after
    dqi_after = calculate_dqi(df)

    # Generate plots
    plots = []
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    for col in numeric_cols:
        safe_name = col.replace(" ", "_")
        plt.figure()
        df[col].hist()
        plt.title(f"{col} Distribution")
        plt.tight_layout()

        filename = f"{safe_name}.png"
        plt.savefig(os.path.join(PLOT_DIR, filename))
        plt.close()

        plots.append(f"plots/{filename}")

    # NLG summary
    nlg_summary = (
        f"The dataset initially had a quality score of {dqi_before}%. "
        f"After handling missing values and duplicates, "
        f"the Dataset Quality Index improved to {dqi_after}%. "
        f"The cleaned dataset is now ready for further analytics."
    )

    return df, dqi_before, dqi_after, plots, nlg_summary
