"""
Migraine Weather Tracker
Serves the single-page weather app for tracking barometric pressure swings
that trigger migraines. All Open-Meteo API calls are made client-side by
the browser so they are unaffected by server-side network restrictions.

Run: python migraine_weather.py
     MIGRAINE_PORT env var overrides the default port 5001.
"""

import os
from flask import Flask, render_template
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    return render_template("migraine_tracker.html")


if __name__ == "__main__":
    port = int(os.environ.get("MIGRAINE_PORT", 5001))
    print(f"\n  Migraine Weather Tracker → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
