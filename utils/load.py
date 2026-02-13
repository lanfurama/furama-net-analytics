import pandas as pd
from pathlib import Path

CSV_2025 = "Spend by Country (1).csv"
CSV_2026 = "Spend by Country.csv"

TX_GROUP_LABELS = {
    10: "Room",
    20: "F&B",
    40: "Recreation",
    50: "Transport/Other",
    60: "Service",
    70: "VAT",
}


def load_data(base_path: Path | None = None) -> pd.DataFrame:
    base = base_path or Path(__file__).resolve().parent.parent
    df_2025 = pd.read_csv(base / CSV_2025)
    df_2025["period"] = 2025
    df_2026 = pd.read_csv(base / CSV_2026)
    df_2026["period"] = 2026
    df = pd.concat([df_2025, df_2026], ignore_index=True)
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")
    df["Net Amount"] = pd.to_numeric(df["Net Amount"], errors="coerce").fillna(0)
    df["Gross Amount"] = pd.to_numeric(df["Gross Amount"], errors="coerce").fillna(0)
    df["Country"] = df["Country"].fillna("").replace("", "N/A").astype(str)
    df["Transaction Code Group"] = pd.to_numeric(df["Transaction Code Group"], errors="coerce")
    df["Room Type"] = df["Room Type"].fillna("").astype(str)
    if "Room Class" in df.columns:
        df["Room Class"] = df["Room Class"].fillna("").astype(str)
    if "Room Class.1" in df.columns:
        df["Room Class.1"] = df["Room Class.1"].fillna("").astype(str)
    return df
