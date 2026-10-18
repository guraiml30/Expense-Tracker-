"""ONE COMMAND:  python runall.py
Runs the full pipeline (data -> clean -> analysis -> charts -> reports),
then deploys the themed EmeraldLedger API + dashboard.

Options:  --port 5000   --no-serve (pipeline only)
"""
import argparse
import webbrowser
import threading
from main import run_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--no-serve", action="store_true")
    args = ap.parse_args()

    print("=" * 56 + "\n  EmeraldLedger - Expense Tracker | runall\n" + "=" * 56)
    run_pipeline()
    if args.no_serve:
        return

    from src.api import app
    url = f"http://127.0.0.1:{args.port}"
    print(f"\nAPI + dashboard live at {url}   (Ctrl+C to stop)")
    print("Try: /api/summary  /api/categories  /api/monthly  /api/overspend  /api/insights")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    main()
