"""Steps 3-6 - Features, analysis, overspend detection, insights, charts."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from src.theme import THEME as T

# Monthly budget per category (Rs). Overspend = spent > budget.
BUDGETS = {"Food": 7000, "Rent": 12000, "Travel": 3500, "Shopping": 5000,
           "Entertainment": 1800, "Utilities": 2000, "Health": 2000, "Education": 1500}


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.weekday >= 5
    return df


def category_totals(df):
    t = df.groupby("category")["amount"].agg(total="sum", count="count", avg="mean")
    t["share_pct"] = (t["total"] / t["total"].sum() * 100).round(1)
    return t.round(2).sort_values("total", ascending=False).reset_index()


def monthly_trend(df):
    m = df.groupby("month")["amount"].sum().rename("total").to_frame()
    m["mom_change_pct"] = (m["total"].pct_change() * 100).round(1)
    m["rolling_3m"] = m["total"].rolling(3).mean().round(2)
    return m.round(2).reset_index()


def overspend_table(df):
    pv = df.pivot_table(index="month", columns="category", values="amount", aggfunc="sum").fillna(0)
    rows = []
    for month, r in pv.iterrows():
        for cat, spent in r.items():
            b = BUDGETS.get(cat)
            if b and spent > b:
                rows.append({"month": month, "category": cat, "spent": round(spent, 2),
                             "budget": b, "over_pct": round((spent - b) / b * 100, 1)})
    return pd.DataFrame(rows, columns=["month", "category", "spent", "budget", "over_pct"]) \
             .sort_values("over_pct", ascending=False).reset_index(drop=True)


def anomalies(df, z=3.0):
    g = df.groupby("category")["amount"]
    zs = (df["amount"] - g.transform("mean")) / g.transform("std")
    return df[zs > z].sort_values("amount", ascending=False)


def summary(df):
    mt = monthly_trend(df)
    return {"total_spend": round(float(df["amount"].sum()), 2),
            "transactions": int(len(df)),
            "avg_monthly": round(float(mt["total"].mean()), 2),
            "avg_transaction": round(float(df["amount"].mean()), 2),
            "top_category": category_totals(df).iloc[0]["category"],
            "peak_month": mt.loc[mt["total"].idxmax(), "month"],
            "lowest_month": mt.loc[mt["total"].idxmin(), "month"]}


def generate_insights(df):
    ct, ov = category_totals(df), overspend_table(df)
    s, out = summary(df), []
    out.append(f"Total spending: Rs {s['total_spend']:,.0f} across {s['transactions']} transactions "
               f"(avg Rs {s['avg_monthly']:,.0f}/month).")
    top = ct.iloc[0]
    out.append(f"{top['category']} is the biggest category ({top['share_pct']}% of spend).")
    out.append(f"Peak month: {s['peak_month']}; lowest month: {s['lowest_month']}.")
    wk = df.groupby("is_weekend")["amount"].mean()
    if True in wk.index and False in wk.index:
        out.append(f"Weekend transactions average Rs {wk[True]:.0f} vs Rs {wk[False]:.0f} on weekdays.")
    if len(ov):
        w = ov.iloc[0]
        out.append(f"Overspending detected in {len(ov)} category-months. Worst: {w['category']} in "
                   f"{w['month']} (+{w['over_pct']}% over budget).")
        out.append(f"Most frequently over budget: {ov['category'].value_counts().idxmax()}.")
    else:
        out.append("No budget overruns detected.")
    out.append("Recommendation: cap the most-overspent category with a weekly limit and "
               "plan festive-season shopping in advance.")
    return out


def make_charts(df, outdir="images"):
    os.makedirs(outdir, exist_ok=True)
    plt.rcParams.update({"figure.facecolor": T["bg"], "axes.facecolor": T["card"],
                         "axes.edgecolor": T["muted"], "axes.labelcolor": T["text"],
                         "text.color": T["text"], "xtick.color": T["muted"],
                         "ytick.color": T["muted"], "axes.titleweight": "bold"})
    ct, mt = category_totals(df), monthly_trend(df)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(ct["category"][::-1], ct["total"][::-1], color=T["primary"])
    ax.set_title("Spending by Category"); ax.set_xlabel("Total (Rs)")
    fig.tight_layout(); fig.savefig(f"{outdir}/01_category_bar.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(ct["total"], labels=ct["category"], autopct="%1.1f%%", colors=T["palette"],
           textprops={"color": T["text"]}, wedgeprops={"edgecolor": T["bg"]})
    ax.set_title("Share of Spending")
    fig.savefig(f"{outdir}/02_category_pie.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(mt["month"], mt["total"], marker="o", color=T["primary"], label="Monthly total")
    ax.plot(mt["month"], mt["rolling_3m"], ls="--", color=T["accent"], label="3-month avg")
    ax.set_title("Monthly Spending Trend"); ax.legend(facecolor=T["card"])
    plt.xticks(rotation=45); fig.tight_layout()
    fig.savefig(f"{outdir}/03_monthly_trend.png", dpi=150); plt.close(fig)

    pv = df.pivot_table(index="category", columns="month", values="amount", aggfunc="sum").fillna(0)
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.heatmap(pv, cmap=sns.light_palette(T["primary"], as_cmap=True), ax=ax,
                cbar_kws={"label": "Rs"})
    ax.set_title("Category x Month Heatmap")
    fig.tight_layout(); fig.savefig(f"{outdir}/04_heatmap.png", dpi=150); plt.close(fig)

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wd = df.groupby("weekday")["amount"].sum().reindex(order)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(wd.index, wd.values, color=T["accent"])
    ax.set_title("Spending by Weekday"); plt.xticks(rotation=30); fig.tight_layout()
    fig.savefig(f"{outdir}/05_weekday.png", dpi=150); plt.close(fig)

    actual = df.groupby("category")["amount"].sum() / df["month"].nunique()
    b = pd.Series(BUDGETS).reindex(actual.index)
    x = np.arange(len(actual)); fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - .2, actual.values, .4, label="Avg actual", color=T["primary"])
    ax.bar(x + .2, b.values, .4, label="Budget", color=T["danger"])
    ax.set_xticks(x); ax.set_xticklabels(actual.index, rotation=30)
    ax.set_title("Average Monthly Spend vs Budget"); ax.legend(facecolor=T["card"])
    fig.tight_layout(); fig.savefig(f"{outdir}/06_budget_vs_actual.png", dpi=150); plt.close(fig)
