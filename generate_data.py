"""Step 1 - Create SYNTHETIC expense data (with realistic mess to clean later)."""
import numpy as np
import pandas as pd

SEED = 42
CATEGORIES = ["Food", "Rent", "Travel", "Shopping", "Entertainment",
              "Utilities", "Health", "Education"]
PAYMENTS = ["UPI", "Card", "Cash", "NetBanking"]


def generate(start="2025-01-01", end="2025-12-31", seed=SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for day in pd.date_range(start, end):
        m, wk = day.month, day.weekday()
        # Rent + utilities + education: fixed, once a month
        if day.day == 1:
            rows.append((day, "Rent", 12000, "NetBanking"))
        if day.day == 5:
            rows.append((day, "Utilities", rng.normal(1800, 250), "UPI"))
        if day.day == 10:
            rows.append((day, "Education", 1500, "UPI"))
        # Food: 1-2 meals/day, pricier on weekends
        for _ in range(rng.integers(1, 3)):
            base = 260 if wk >= 5 else 170
            rows.append((day, "Food", rng.lognormal(np.log(base), 0.35),
                         rng.choice(PAYMENTS, p=[.55, .2, .2, .05])))
        # Travel: commute-ish, bigger trip in May and December
        if rng.random() < 0.35:
            rows.append((day, "Travel", rng.lognormal(np.log(220), 0.4), "UPI"))
        if (m in (5, 12)) and day.day == 15:
            rows.append((day, "Travel", rng.normal(6500, 800), "Card"))
        # Shopping: festive spike Oct-Nov
        p = 0.30 if m in (10, 11) else 0.10
        if rng.random() < p:
            mult = 2.2 if m in (10, 11) else 1.0
            rows.append((day, "Shopping", rng.lognormal(np.log(900 * mult), 0.5), "Card"))
        # Entertainment: weekends
        if wk >= 5 and rng.random() < 0.45:
            rows.append((day, "Entertainment", rng.lognormal(np.log(500), 0.4),
                         rng.choice(["UPI", "Card"])))
        # Health: rare
        if rng.random() < 0.03:
            rows.append((day, "Health", rng.lognormal(np.log(1200), 0.5), "UPI"))

    df = pd.DataFrame(rows, columns=["date", "category", "amount", "payment_method"])
    df["amount"] = df["amount"].round(2)

    # --- inject dirty data so the cleaning step has real work ---
    dirty = df.copy()
    dirty["date"] = dirty["date"].dt.strftime("%Y-%m-%d")
    n = len(dirty)
    dirty.loc[rng.choice(n, 25, replace=False), "payment_method"] = np.nan   # missing
    idx = rng.choice(n, 40, replace=False)
    dirty.loc[idx, "category"] = dirty.loc[idx, "category"].str.upper()      # casing
    idx = rng.choice(n, 20, replace=False)
    dirty.loc[idx, "category"] = " " + dirty.loc[idx, "category"] + " "      # spaces
    dirty = pd.concat([dirty, dirty.sample(15, random_state=1)])             # duplicates
    dirty.loc[rng.choice(len(dirty), 5, replace=False), "amount"] = -50      # invalid
    return dirty.sample(frac=1, random_state=3).reset_index(drop=True)


if __name__ == "__main__":
    out = generate()
    out.to_csv("data/expenses_raw.csv", index=False)
    print(f"Raw data created: {len(out)} rows -> data/expenses_raw.csv")
