# Cloud-Based Electricity Usage Monitor

A beginner-friendly cloud computing mini-project built with **Python Flask**, **SQLite**, HTML/CSS, and Chart.js. It records electricity readings, displays usage by device, charts daily usage, and estimates energy cost.

## Features

- Dashboard showing total recorded kWh, today's recorded kWh, and estimated cost.
- Add a reading for any device or room.
- Simulate a sample reading for demonstration.
- View all saved readings.
- Daily usage line chart and device-wise totals.
- SQLite database is created automatically on first run.
- Prepared for deployment to a Python web host that supports Flask.

## Requirements

- Python 3.10 or newer
- Internet connection for the Chart.js CDN and Google Fonts (the app itself runs locally without those visual assets)

## Run on Windows (VS Code)

1. Extract the ZIP file.
2. Open the extracted `cloud_electricity_usage_monitor` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

5. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python app.py
   ```

7. Open **http://127.0.0.1:5000** in your browser.

The first run creates `electricity.db` and inserts sample readings. The database file is intentionally excluded from version control; your app creates it automatically.

## Cloud deployment outline

This project includes a `Procfile` for a host that supports Python web services.

1. Push the project folder to a GitHub repository.
2. Create a new Python web service on a hosting provider that supports Flask applications.
3. Connect the repository.
4. Set the build/install command to `pip install -r requirements.txt`.
5. Set the start command to `gunicorn app:app` (the included Procfile uses this command).
6. If the provider has an ephemeral filesystem, configure a persistent disk or managed database for readings. SQLite data may be lost when a temporary deployment instance restarts or redeploys.

**Important:** Deployment steps and free-tier availability depend on the hosting provider and may change. This ZIP is the project source code; it has not been deployed to a live cloud URL.

## How the project works

1. User enters a device name and energy amount in kWh.
2. Flask validates the input and stores the timestamp, device, and energy value in SQLite.
3. The dashboard queries the database and calculates totals.
4. Chart.js visualizes daily consumption in the browser.
5. Estimated cost = total recorded kWh × configured tariff.

## Change the tariff

Open `app.py` and change:

```python
RATE_PER_KWH = 6.50
```

This is a sample tariff for demonstration only. Replace it with the tariff applicable to your electricity provider. Real bills may include slabs, fixed charges, taxes, and other adjustments, so the displayed amount is only an estimate.

## Project structure

```text
cloud_electricity_usage_monitor/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── add_reading.html
│   └── readings.html
└── static/
    └── style.css
```

## Project limitations

- Readings are manually entered or simulated; this project does not connect to a physical smart meter.
- The app is a learning prototype, not a utility-grade billing system.
- Before public production use, configure a strong secret key, HTTPS, authentication, access controls, backups, and a persistent database.
