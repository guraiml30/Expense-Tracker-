# EmeraldLedger - Expense Tracker App using Data Science

End-to-end data science project that generates synthetic expense data, cleans it, analyses spending patterns, detects budget overspending, and serves results through a **themed REST API + web dashboard**.

## Problem
People and small businesses rarely know where money goes. Raw expense logs are messy (duplicates, missing values, inconsistent labels) and hard to act on.

## Solution
An automated pipeline: **input -> cleaning -> feature engineering -> analysis -> visualization -> insights -> decisions**, runnable with one command (`python runall.py`).

## Features
- Synthetic data generator with realistic patterns (rent, weekend food spikes, festive shopping, trips)
- Cleaning: dedupe, casing/whitespace fixes, missing values, invalid amounts, outlier flags
- Category analysis, monthly trend + 3-month rolling average, weekday patterns
- Budget vs actual and **overspend detection**, z-score anomaly detection
- Auto-generated insights (`outputs/insights.txt`)
- Flask REST API + dark emerald/gold dashboard, with an "Add expense" form
- Optional Streamlit dashboard (`streamlit run dashboard.py`)

## Tech Stack
Python, Pandas, NumPy, Matplotlib, Seaborn, Flask, Chart.js, Streamlit (optional)

## How to Run
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python runall.py               # pipeline + API at http://127.0.0.1:5000
python runall.py --no-serve    # pipeline only
```

## API
| Endpoint | Description |
|---|---|
| GET `/` | Themed dashboard |
| GET `/api/summary` | KPIs |
| GET `/api/categories` | Totals and share by category |
| GET `/api/monthly` | Monthly totals, MoM %, rolling avg |
| GET `/api/overspend` | Budget overruns |
| GET `/api/insights` | Text insights |
| GET `/api/expenses?category=Food&limit=10` | Recent expenses |
| POST `/api/expenses` | Add expense `{"category","amount","date","payment_method"}` |

## Results
Add your screenshots here (from `images/`):

![Category](images/01_category_bar.png)
![Trend](images/03_monthly_trend.png)
![Budget](images/06_budget_vs_actual.png)

## Project Structure
```
data/ notebooks/ src/ outputs/ images/ docs/
main.py  runall.py  dashboard.py  requirements.txt
```

## Future Improvements
Mobile app, real-time tracking, ML spending forecast, budget alerts, savings goal tracking.

## Author
Your Name - GitHub | LinkedIn
