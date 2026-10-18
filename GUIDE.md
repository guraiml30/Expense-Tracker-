# Expense Tracker - Complete Student Guide

## 1. Project Explanation
**Simple:** An expense tracker records what you spend, groups it, and shows where your money goes so you can spend smarter.
**Technical:** A data pipeline (ingest -> clean -> feature engineering -> aggregation -> visualization -> rule/statistics-based insights) exposed through a REST API.
**Uses:** personal finance, business expense monitoring, budgeting and cost control, financial planning.
**Workflow:** data input -> storage (CSV) -> analysis (Pandas) -> visualization -> insights -> decisions (cut/cap/plan).

## 2. Tech Stack Options
| Option | Stack | Dashboard | Difficulty |
|---|---|---|---|
| A Easy | Python, Pandas, Matplotlib, CSV | No | Low |
| B Intermediate | + Seaborn, Flask API, Chart.js | Yes (web) | Medium |
| C Advanced | + SQL DB, Streamlit/Power BI, scikit-learn forecasting | Yes | High |

**Chosen: Option B** (this repo): shows analysis + API + dashboard without heavy setup.

## 3. Architecture
```
[Synthetic generator / User input (POST)]
        |  date, category, amount, payment_method
        v
   data/expenses_raw.csv
        |  clean.py (dedupe, fix labels, nulls, invalid, outliers)
        v
   data/expenses_clean.csv
        |  analyze.py (features, totals, trends, overspend, anomalies)
        v
 outputs/*.csv  images/*.png  insights.txt
        |
        v
   api.py (Flask) -> dashboard (/)  +  JSON endpoints
```

## 4. Implementation Plan
| Phase | Do | Why | Output | Avoid |
|---|---|---|---|---|
| 1 Setup | venv, install, folders | reproducible | repo skeleton | installing globally |
| 2 Data | run generate_data.py | no real data | expenses_raw.csv | perfectly clean data |
| 3 Cleaning | clean.py | trustworthy numbers | expenses_clean.csv + log | deleting outliers blindly |
| 4 EDA | describe, counts, distributions | understand data | summary tables | skipping checks |
| 5 Features | month, weekday, weekend | enable trends | new columns | leaking future data |
| 6 Analysis | totals, MoM, budget | answer questions | CSV reports | unexplained metrics |
| 7 Visualization | 6 charts | communicate | images/*.png | cluttered, unlabeled charts |
| 8 Insights | rule-based text | decisions | insights.txt | numbers without meaning |
| 9 GitHub | commit, push, README | proof | public repo | committing venv |

## 5. Folder Structure
- `data/` raw + clean CSVs  - `notebooks/` optional exploration notebooks
- `src/` modules (generate, clean, analyze, api, theme)  - `outputs/` reports/insights
- `images/` charts (README screenshots)  - `main.py` pipeline  - `runall.py` pipeline + API
- `dashboard.py` Streamlit option  - `requirements.txt`, `README.md`, `.gitignore`

## 6. Installation
Install Python 3.10+ from python.org (tick "Add to PATH" on Windows).
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Mac / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 7. Full Code
All code is in `src/`, `main.py`, `runall.py`, `dashboard.py` and is commented.

## 8. Virtual Simulation
1. Loop over every day of 2025.  2. Add fixed items (rent day 1, utilities day 5, fees day 10).
3. Add random daily food (higher on weekends), commute travel (35% of days), trips in May/Dec.
4. Shopping probability triples and spends double in Oct-Nov (festive trend).
5. Inject mess: nulls, case/space errors, duplicates, negative amounts.
6. Clean, then compare monthly category totals with BUDGETS -> overspend if spent > budget.
7. Output reports, charts, insights.

## 9. How to Run
```bash
python runall.py            # everything + API on :5000
python main.py              # pipeline only
streamlit run dashboard.py  # optional
```
Expect: cleaning log (~806 raw -> ~786 clean rows), 6 PNGs in images/, 5 files in outputs/, dashboard opens in browser.

## 10. GitHub Upload
```bash
git init
git add .
git commit -m "feat: initial expense tracker pipeline"
git branch -M main
git remote add origin https://github.com/<username>/Expense-Tracker-App.git
git push -u origin main
```
**Repo name:** Expense-Tracker-App-Data-Science
**Description:** End-to-end expense analytics: synthetic data, cleaning, overspend detection, Flask API and themed dashboard.
**Topics:** python, pandas, data-analysis, data-visualization, finance, flask, expense-tracker, portfolio-project

## 11. README
See `README.md`.

## 12. Proof Plan
| Day | Task | Commit message | Proof |
|---|---|---|---|
| 1 | Setup, folders, requirements | chore: project setup | repo tree |
| 2 | generate_data + clean | feat: synthetic data and cleaning | raw vs clean preview |
| 3 | analyze.py | feat: analysis and overspend detection | terminal insights |
| 4 | charts + API | feat: visualizations and themed API | chart PNGs, dashboard |
| 5 | README, polish, push | docs: README and screenshots | final repo page |

## 13. Screenshots to Capture
Dataset preview (raw vs clean `head()`), terminal cleaning log, category bar, pie, monthly trend, heatmap, budget vs actual, dashboard at `/`, `/api/summary` JSON, overspend table.

## 14. Interview Preparation
1. **What does the project do?** Cleans and analyses expenses, flags overspending, serves insights via API.
2. **Why synthetic data?** No real data access; generator encodes known patterns so I can verify the analysis finds them.
3. **How did you clean data?** Dedupe, standardize labels, fill missing payment method, drop invalid amounts, flag outliers via IQR.
4. **Why flag outliers instead of deleting?** A big expense (trip, rent) can be real; deletion would hide true spending.
5. **How is overspend detected?** Monthly category sum vs a budget; over_pct = (spent - budget)/budget.
6. **What is the rolling average for?** Smooths noise to show the real trend.
7. **Which features did you engineer?** month, weekday, is_weekend.
8. **What insight surprised you?** Festive months drive a large shopping spike; Food is most often over budget.
9. **How would you scale it?** SQL database, scheduled jobs, auth on API, real bank/UPI imports.
10. **What would you improve?** Forecasting with time-series/ML, alerts, goal tracking.

**HR answer:** "I built a tool that turns messy expense records into clear insights and budget alerts, and deployed it as a dashboard anyone can use."
**Technical answer:** "A Pandas pipeline (generate, clean, feature-engineer, aggregate) feeding a Flask JSON API and Chart.js dashboard, with statistical anomaly and budget-rule detection."

## 15. Future Improvements
Mobile app, real-time tracking (UPI/SMS parsing), AI spending prediction (Prophet/ARIMA), budget alerts (email/WhatsApp), savings goal tracking, user login and multi-user DB.

## 16. Troubleshooting
| Error | Fix |
|---|---|
| `ModuleNotFoundError: src` | Run commands from the project root |
| `pip not recognized` | Use `python -m pip install -r requirements.txt` |
| Port 5000 in use (Mac AirPlay) | `python runall.py --port 5055` |
| Dashboard charts blank | Needs internet for Chart.js CDN; check browser console |
| `FileNotFoundError: expenses_clean.csv` | Run `python main.py` first (runall does this) |
| Matplotlib backend error | Already set to Agg in analyze.py |
| venv activate blocked on Windows | `Set-ExecutionPolicy -Scope Process RemoteSigned` |
| git push rejected | `git pull origin main --rebase` then push |
