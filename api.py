"""EmeraldLedger API + themed dashboard (Flask).
Endpoints: /  /api/health  /api/summary  /api/categories  /api/monthly
           /api/overspend  /api/insights  /api/expenses (GET, POST)  /images/<file>
"""
import os
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, Response
from src import analyze as A
from src.theme import THEME as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "data", "expenses_clean.csv")
app = Flask(__name__)


def load():
    return A.add_features(pd.read_csv(CSV))


@app.get("/api/health")
def health():
    return jsonify(status="ok", app="EmeraldLedger Expense Tracker")


@app.get("/api/summary")
def summary():
    return jsonify(A.summary(load()))


@app.get("/api/categories")
def categories():
    return jsonify(A.category_totals(load()).to_dict("records"))


@app.get("/api/monthly")
def monthly():
    return jsonify(A.monthly_trend(load()).fillna(0).to_dict("records"))


@app.get("/api/overspend")
def overspend():
    return jsonify(A.overspend_table(load()).to_dict("records"))


@app.get("/api/insights")
def insights():
    return jsonify(A.generate_insights(load()))


@app.route("/api/expenses", methods=["GET", "POST"])
def expenses():
    if request.method == "POST":           # simple USER INPUT: add one expense
        d = request.get_json(force=True)
        try:
            amt = float(d["amount"]); cat = str(d["category"]).strip().title()
            date = pd.to_datetime(d.get("date") or pd.Timestamp.today()).strftime("%Y-%m-%d")
        except Exception:
            return jsonify(error="need valid category, amount (and optional date)"), 400
        if amt <= 0:
            return jsonify(error="amount must be positive"), 400
        row = pd.DataFrame([{"date": date, "category": cat, "amount": amt,
                             "payment_method": d.get("payment_method", "UPI"),
                             "is_outlier": False}])
        row.to_csv(CSV, mode="a", header=False, index=False)
        return jsonify(message="expense added", expense=row.iloc[0].to_dict()), 201
    df = load()
    if request.args.get("category"):
        df = df[df.category.str.lower() == request.args["category"].lower()]
    n = int(request.args.get("limit", 20))
    out = df.sort_values("date", ascending=False).head(n).copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    return jsonify(out[["date", "category", "amount", "payment_method"]].to_dict("records"))


@app.get("/images/<path:name>")
def images(name):
    return send_from_directory(os.path.join(ROOT, "images"), name)


@app.get("/")
def home():
    html = PAGE
    for k in ("bg", "card", "text", "muted", "primary", "accent", "danger"):
        html = html.replace("{{" + k + "}}", T[k])
    return Response(html.replace("{{palette}}", str(T["palette"])), mimetype="text/html")


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EmeraldLedger - Expense Tracker</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1"></script>
<style>
:root{--bg:{{bg}};--card:{{card}};--text:{{text}};--muted:{{muted}};--p:{{primary}};--a:{{accent}};--d:{{danger}}}
*{box-sizing:border-box}body{margin:0;font-family:Segoe UI,system-ui,sans-serif;background:var(--bg);color:var(--text)}
header{padding:22px 28px;border-bottom:2px solid var(--p);display:flex;justify-content:space-between;align-items:center}
h1{margin:0;font-size:24px}h1 span{color:var(--p)}.tag{color:var(--muted);font-size:13px}
main{padding:24px;max-width:1200px;margin:auto}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.card{background:var(--card);border-radius:14px;padding:18px;border:1px solid #1d4457}
.kpi .v{font-size:26px;font-weight:700;color:var(--a);margin-top:6px}.kpi .l{color:var(--muted);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px;margin-top:14px}
h3{margin:0 0 12px;color:var(--p);font-size:16px}
ul{padding-left:18px;margin:0;line-height:1.7}table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:7px;border-bottom:1px solid #1d4457}th{color:var(--muted)}
.bad{color:var(--d);font-weight:600}input,select,button{padding:9px;border-radius:8px;border:1px solid #1d4457;background:var(--bg);color:var(--text)}
button{background:var(--p);color:#04231a;font-weight:700;cursor:pointer;border:0}
form{display:flex;gap:8px;flex-wrap:wrap}img{width:100%;border-radius:10px}
</style></head><body>
<header><h1>Emerald<span>Ledger</span> Expense Tracker</h1><div class="tag">Data Science Dashboard | live API</div></header>
<main>
<div class="kpis" id="kpis"></div>
<div class="grid">
 <div class="card"><h3>Spending by Category</h3><canvas id="c1"></canvas></div>
 <div class="card"><h3>Monthly Trend</h3><canvas id="c2"></canvas></div>
</div>
<div class="grid">
 <div class="card"><h3>Insights</h3><ul id="ins"></ul></div>
 <div class="card"><h3>Overspend Alerts (top 8)</h3><table id="ov"></table></div>
</div>
<div class="card" style="margin-top:14px"><h3>Add an Expense</h3>
<form id="f"><input name="category" placeholder="Category" required>
<input name="amount" type="number" step="0.01" placeholder="Amount (Rs)" required>
<input name="date" type="date"><select name="payment_method"><option>UPI</option><option>Card</option><option>Cash</option><option>NetBanking</option></select>
<button>Add</button><span id="msg" class="tag"></span></form></div>
<div class="grid"><div class="card"><h3>Budget vs Actual</h3><img src="/images/06_budget_vs_actual.png"></div>
<div class="card"><h3>Category x Month Heatmap</h3><img src="/images/04_heatmap.png"></div></div>
</main>
<script>
const P={{palette}};const $=id=>document.getElementById(id);
const j=u=>fetch(u).then(r=>r.json());let c1,c2;
async function load(){
 const s=await j('/api/summary');
 $('kpis').innerHTML=[['Total Spend','Rs '+Math.round(s.total_spend).toLocaleString()],['Avg / Month','Rs '+Math.round(s.avg_monthly).toLocaleString()],
 ['Transactions',s.transactions],['Top Category',s.top_category],['Peak Month',s.peak_month]].map(x=>`<div class="card kpi"><div class="l">${x[0]}</div><div class="v">${x[1]}</div></div>`).join('');
 const c=await j('/api/categories');c1&&c1.destroy();
 c1=new Chart($('c1'),{type:'doughnut',data:{labels:c.map(x=>x.category),datasets:[{data:c.map(x=>x.total),backgroundColor:P,borderColor:'{{bg}}'}]},options:{plugins:{legend:{labels:{color:'{{text}}'}}}}});
 const m=await j('/api/monthly');c2&&c2.destroy();
 c2=new Chart($('c2'),{type:'line',data:{labels:m.map(x=>x.month),datasets:[{label:'Total',data:m.map(x=>x.total),borderColor:'{{primary}}',tension:.3},{label:'3m avg',data:m.map(x=>x.rolling_3m||null),borderColor:'{{accent}}',borderDash:[6,4],tension:.3}]},options:{scales:{x:{ticks:{color:'{{muted}}'}},y:{ticks:{color:'{{muted}}'}}},plugins:{legend:{labels:{color:'{{text}}'}}}}});
 $('ins').innerHTML=(await j('/api/insights')).map(i=>`<li>${i}</li>`).join('');
 const o=(await j('/api/overspend')).slice(0,8);
 $('ov').innerHTML='<tr><th>Month</th><th>Category</th><th>Spent</th><th>Over</th></tr>'+o.map(r=>`<tr><td>${r.month}</td><td>${r.category}</td><td>${Math.round(r.spent)}</td><td class="bad">+${r.over_pct}%</td></tr>`).join('');
}
$('f').onsubmit=async e=>{e.preventDefault();const d=Object.fromEntries(new FormData(e.target));
 const r=await fetch('/api/expenses',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
 $('msg').textContent=r.ok?'Added!':'Invalid input';if(r.ok){e.target.reset();load();}};
load();
</script></body></html>"""
