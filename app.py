from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_PATH = Path(__file__).with_name("electricity.db")
RATE_PER_KWH = 6.50  # Example tariff in INR per kWh; change to your local tariff.

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                device TEXT NOT NULL,
                energy_kwh REAL NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
        if count == 0:
            # Seed sample readings so the dashboard works on first launch.
            now = datetime.now()
            devices = ["Living Room", "Kitchen", "Air Conditioner", "Water Heater"]
            for day in range(13, -1, -1):
                for device in devices:
                    value = round(random.uniform(0.3, 3.2), 2)
                    recorded = (now - timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S")
                    conn.execute(
                        "INSERT INTO readings (recorded_at, device, energy_kwh) VALUES (?, ?, ?)",
                        (recorded, device, value)
                    )

@app.route("/")
def dashboard():
    with connect_db() as conn:
        total = conn.execute("SELECT COALESCE(SUM(energy_kwh), 0) FROM readings").fetchone()[0]
        today = datetime.now().strftime("%Y-%m-%d")
        today_total = conn.execute(
            "SELECT COALESCE(SUM(energy_kwh), 0) FROM readings WHERE substr(recorded_at, 1, 10) = ?",
            (today,)
        ).fetchone()[0]
        devices = conn.execute("""
            SELECT device, ROUND(SUM(energy_kwh), 2) AS usage
            FROM readings GROUP BY device ORDER BY usage DESC
        """).fetchall()
        recent = conn.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT 10"
        ).fetchall()
        daily = conn.execute("""
            SELECT substr(recorded_at, 1, 10) AS day, ROUND(SUM(energy_kwh), 2) AS usage
            FROM readings GROUP BY day ORDER BY day DESC LIMIT 7
        """).fetchall()
    estimated_bill = total * RATE_PER_KWH
    return render_template(
        "dashboard.html",
        total=round(total, 2),
        today_total=round(today_total, 2),
        estimated_bill=round(estimated_bill, 2),
        devices=devices,
        recent=recent,
        daily=list(reversed(daily)),
        rate=RATE_PER_KWH
    )

@app.route("/add", methods=["GET", "POST"])
def add_reading():
    if request.method == "POST":
        device = request.form.get("device", "").strip()
        try:
            energy = float(request.form.get("energy_kwh", ""))
        except ValueError:
            energy = -1
        if not device:
            flash("Please enter a device or room name.", "error")
        elif energy <= 0 or energy > 10000:
            flash("Energy usage must be greater than 0 and no more than 10,000 kWh.", "error")
        else:
            with connect_db() as conn:
                conn.execute(
                    "INSERT INTO readings (recorded_at, device, energy_kwh) VALUES (?, ?, ?)",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device, round(energy, 2))
                )
            flash("Electricity reading added successfully.", "success")
            return redirect(url_for("dashboard"))
    return render_template("add_reading.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    device = random.choice(["Living Room", "Kitchen", "Air Conditioner", "Water Heater"])
    energy = round(random.uniform(0.2, 2.5), 2)
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO readings (recorded_at, device, energy_kwh) VALUES (?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device, energy)
        )
    flash(f"Simulated {energy} kWh reading for {device}.", "success")
    return redirect(url_for("dashboard"))

@app.route("/readings")
def readings():
    with connect_db() as conn:
        rows = conn.execute("SELECT * FROM readings ORDER BY recorded_at DESC").fetchall()
    return render_template("readings.html", readings=rows)

init_db()

if __name__ == "__main__":
    app.run(debug=True)
