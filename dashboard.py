"""Optional Streamlit dashboard:  streamlit run dashboard.py"""
import pandas as pd, streamlit as st
from src import analyze as A

st.set_page_config(page_title="Expense Tracker", layout="wide")
df = A.add_features(pd.read_csv("data/expenses_clean.csv"))
st.title("Expense Tracker - Data Science")
cats = st.multiselect("Categories", sorted(df.category.unique()), sorted(df.category.unique()))
df = df[df.category.isin(cats)]
s = A.summary(df)
c1, c2, c3 = st.columns(3)
c1.metric("Total", f"Rs {s['total_spend']:,.0f}")
c2.metric("Avg / month", f"Rs {s['avg_monthly']:,.0f}")
c3.metric("Top category", s["top_category"])
st.bar_chart(A.category_totals(df).set_index("category")["total"])
st.line_chart(A.monthly_trend(df).set_index("month")["total"])
st.dataframe(A.overspend_table(df))
