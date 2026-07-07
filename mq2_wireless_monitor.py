"""
MQ2 gas/smoke sensor wireless monitoring for Raspberry Pi.

This turns the Pi into a small web server, so you can check the
gas sensor's live status from any phone, tablet, or computer on the
same Wi-Fi network, without needing to be plugged into the Pi
directly.

It uses the MQ2 sensor's digital DO pin (gas detected or not) and
also keeps a log file, same as mq2_gas_logger.py, but adds a live
web page and a JSON API endpoint on top.

Wiring:
    MQ2 VCC -> 5V
    MQ2 GND -> GND
    MQ2 DO  -> GPIO17

Install Flask first if needed:
    pip3 install flask

Run with:
    python3 mq2_wireless_monitor.py

Then, from any device on the same network, open a browser and go to:
    http://<your-pi-ip-address>:5000

To find your Pi's IP address, run this on the Pi itself:
    hostname -I

Stop with Ctrl+C
"""

from gpiozero import DigitalInputDevice
from flask import Flask, jsonify, render_template_string
from datetime import datetime
from threading import Thread
from time import sleep
import csv
import os

LOG_FILE = "gas_log.csv"
gas_sensor = DigitalInputDevice(17)

app = Flask(__name__)

latest_reading = {
    "status": "starting up",
    "timestamp": None
}

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gas Sensor Monitor</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 60px; }
        .status { font-size: 32px; padding: 20px; border-radius: 8px; display: inline-block; }
        .normal { background-color: #d9f2d9; color: #1a5e1a; }
        .alert { background-color: #f7d6d6; color: #8a1c1c; }
        .timestamp { margin-top: 20px; color: #555; }
    </style>
</head>
<body>
    <h1>MQ2 Gas Sensor Monitor</h1>
    <div class="status {{ css_class }}">{{ status }}</div>
    <div class="timestamp">Last updated: {{ timestamp }}</div>
    <p>This page refreshes automatically every 3 seconds.</p>
</body>
</html>
"""


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "status"])


def log_reading(status):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(timespec="seconds"), status])


def sensor_loop():
    global latest_reading
    ensure_log_file()
    print("Warming up sensor, please wait...")
    sleep(20)
    print("Sensor loop started")

    while True:
        status = "GAS DETECTED" if gas_sensor.value == 1 else "normal"
        timestamp = datetime.now().isoformat(timespec="seconds")

        latest_reading = {"status": status, "timestamp": timestamp}
        log_reading(status)

        sleep(2)


@app.route("/")
def index():
    css_class = "alert" if latest_reading["status"] == "GAS DETECTED" else "normal"
    return render_template_string(
        PAGE_TEMPLATE,
        status=latest_reading["status"],
        timestamp=latest_reading["timestamp"],
        css_class=css_class,
    )


@app.route("/api/reading")
def api_reading():
    return jsonify(latest_reading)


if __name__ == "__main__":
    sensor_thread = Thread(target=sensor_loop, daemon=True)
    sensor_thread.start()

    # host="0.0.0.0" makes this reachable from other devices on the
    # network, not just from the Pi itself
    app.run(host="0.0.0.0", port=5000)
