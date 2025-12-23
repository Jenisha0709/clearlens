import os
import pandas as pd
import matplotlib.pyplot as plt

# ==================================================
# PATH SETUP
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "dirty_cafe_sales.csv")
CLEAN_PATH = os.path.join(BASE_DIR, "..", "data", "cleaned_dirty_cafe_sales.csv")
PLOT_DIR = os.path.join(BASE_DIR, "..", "outputs")

os.makedirs(PLOT_DIR, exist_ok=True)

# ==================================================
# LOAD DATASET
# ==================================================
df = pd.read_csv(DATA_PATH)

print("ORIGINAL DATASET")
print(df.head())
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
print("-" * 60)

original_rows = df.shape[0]

# ==================================================
# SMART NUMERIC RECOVERY (REAL-WORLD LOGIC)
# ==================================================
for col in df.columns:
    try:
        converted = pd.to_numeric(df[col], errors="coerce")
        # Keep numeric conversion only if meaningful
        if converted.notna().mean() > 0.5:
            df[col] = converted
    except Exception:
        pass

# ==================================================
# DQI BEFORE CLEANING
# ==================================================
missing_before = df.isnull().mean().mean() * 100
duplicate_before = df.duplicated().sum() / df.shape[0] * 100
DQI_before = 100 - (missing_before + duplicate_before)

print("DQI BEFORE CLEANING:", round(DQI_before, 2))
print("-" * 60)

# ==================================================
# DUPLICATE HANDLING
# ==================================================
df = df.drop_duplicates()

# ==================================================
# ADAPTIVE CLEANING STRATEGY SELECTION (ACSS)
# ==================================================
def adaptive_numeric_imputation(series):
    missing_ratio = series.isnull().mean()
    skewness = series.skew()

    if missing_ratio > 0.3:
        return series.fillna(series.median()), "median"

    if abs(skewness) < 0.5:
        return series.fillna(series.mean()), "mean"

    return series.fillna(series.median()), "median"


def adaptive_categorical_imputation(series):
    missing_ratio = series.isnull().mean()

    if missing_ratio > 0.3:
        return series.fillna("Unknown"), "unknown"

    value_freq = series.value_counts(normalize=True)

    if not value_freq.empty and value_freq.iloc[0] > 0.5:
        return series.fillna(series.mode()[0]), "mode"

    return series.fillna("Unknown"), "unknown"


print("ADAPTIVE CLEANING STRATEGY SELECTION")
print("-" * 60)

for col in df.columns:
    if df[col].dtype in ["int64", "float64"]:
        df[col], method = adaptive_numeric_imputation(df[col])
        print(f"{col}: numeric → {method}")
    else:
        df[col], method = adaptive_categorical_imputation(df[col])
        print(f"{col}: categorical → {method}")

print("-" * 60)

# ==================================================
# IDENTIFY NUMERIC COLUMNS (POST-CLEANING)
# ==================================================
numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

# ==================================================
# OUTLIER HANDLING (ONLY IF NUMERIC EXISTS)
# ==================================================
def remove_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[column] >= lower) & (df[column] <= upper)]

if len(numeric_columns) > 0:
    for col in numeric_columns:
        before = df.shape[0]
        df = remove_outliers_iqr(df, col)
        after = df.shape[0]
        print(f"Outliers removed from {col}: {before - after}")
else:
    print("No numeric columns available for outlier detection.")

print("-" * 60)

# ==================================================
# DQI AFTER CLEANING
# ==================================================
missing_after = df.isnull().mean().mean() * 100
DQI_after = 100 - missing_after

print("DQI AFTER CLEANING:", round(DQI_after, 2))
print("-" * 60)

# ==================================================
# SAVE CLEANED DATA
# ==================================================
df.to_csv(CLEAN_PATH, index=False)
print("Cleaned dataset saved at:")
print(CLEAN_PATH)
print("-" * 60)

# ==================================================
# AUTOMATED ANALYTICS (SAFE)
# ==================================================
print("AUTOMATED ANALYTICS")
print("-" * 60)

if len(numeric_columns) > 0:
    print("Descriptive Statistics:")
    print(df[numeric_columns].describe())
else:
    print("No numeric columns available for statistical analysis.")

print("-" * 60)

# ==================================================
# AUTOMATED VISUALIZATION (SAFE)
# ==================================================
print("GENERATING VISUALIZATIONS")

if len(numeric_columns) > 0:
    for col in numeric_columns:
        plt.figure()
        df[col].hist()
        plt.title(f"Distribution of {col}")
        plt.savefig(os.path.join(PLOT_DIR, f"{col}_histogram.png"))
        plt.close()

    plt.figure()
    df[numeric_columns].boxplot()
    plt.title("Boxplot of Numeric Attributes")
    plt.savefig(os.path.join(PLOT_DIR, "boxplot.png"))
    plt.close()
else:
    print("Skipping visualizations: no numeric columns detected.")

print("-" * 60)

# ==================================================
# NATURAL-LANGUAGE INSIGHTS
# ==================================================
print("AUTO-GENERATED INSIGHTS")
print("-" * 60)

print(f"Dataset size after cleaning: {df.shape[0]} records.")
print("Adaptive preprocessing completed successfully.")
print("The system robustly handled real-world noisy and mixed-type data.")
print("-" * 60)

print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
