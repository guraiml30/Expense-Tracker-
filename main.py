"""Pipeline: generate -> clean -> features -> analyze -> charts -> reports."""
import json, os
import pandas as pd
from src.generate_data import generate
from src.clean import clean
from src import analyze as A


def run_pipeline():
    for d in ("data", "outputs", "images"):
        os.makedirs(d, exist_ok=True)

    print("[1/5] Generating synthetic data...")
    raw = generate(); raw.to_csv("data/expenses_raw.csv", index=False)

    print("[2/5] Cleaning data...")
    df = clean(raw); log = df.attrs["log"]
    df.to_csv("data/expenses_clean.csv", index=False)
    print("      ", log)

    print("[3/5] Feature engineering...")
    df = A.add_features(df)

    print("[4/5] Analysis + reports...")
    A.category_totals(df).to_csv("outputs/category_summary.csv", index=False)
    A.monthly_trend(df).to_csv("outputs/monthly_trend.csv", index=False)
    A.overspend_table(df).to_csv("outputs/overspend_report.csv", index=False)
    A.anomalies(df).to_csv("outputs/anomalies.csv", index=False)
    insights = A.generate_insights(df)
    with open("outputs/insights.txt", "w") as f:
        f.write("\n".join(f"- {i}" for i in insights))
    with open("outputs/summary.json", "w") as f:
        json.dump({**A.summary(df), "cleaning_log": log}, f, indent=2)

    print("[5/5] Creating charts...")
    A.make_charts(df, "images")

    print("\nKEY INSIGHTS")
    for i in insights:
        print(" *", i)
    print("\nPipeline complete. See outputs/ and images/.")
    return df


if __name__ == "__main__":
    run_pipeline()
