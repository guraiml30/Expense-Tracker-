"""Step 2 - Data cleaning."""
import pandas as pd


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    log = {"rows_raw": len(df)}
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["category"] = df["category"].astype(str).str.strip().str.title()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["payment_method"] = df["payment_method"].fillna("Unknown")

    log["duplicates_removed"] = int(df.duplicated().sum())
    df = df.drop_duplicates()
    bad = df["date"].isna() | df["amount"].isna() | (df["amount"] <= 0)
    log["invalid_removed"] = int(bad.sum())
    df = df[~bad]

    # Flag (not delete) outliers: > Q3 + 3*IQR within each category
    q1 = df.groupby("category")["amount"].transform(lambda s: s.quantile(.25))
    q3 = df.groupby("category")["amount"].transform(lambda s: s.quantile(.75))
    df["is_outlier"] = df["amount"] > q3 + 3 * (q3 - q1)
    log["outliers_flagged"] = int(df["is_outlier"].sum())
    log["rows_clean"] = len(df)

    df = df.sort_values("date").reset_index(drop=True)
    df.attrs["log"] = log
    return df
