"""
MQ2 gas/smoke sensor data logger for Raspberry Pi.

The MQ2 sensor detects LPG, smoke, alcohol, propane, and other
combustible gases. Most MQ2 modules have four pins: VCC, GND, DO
(digital output), and AO (analog output).

This script uses the DO pin for a simple threshold-based reading
(gas detected or not) and logs each reading with a timestamp to a
CSV file, so you can review gas levels over time even if you were
not watching the terminal when something happened.

Wiring (digital mode):
    MQ2 VCC -> 5V
    MQ2 GND -> GND
    MQ2 DO  -> GPIO17

Most MQ2 modules have an onboard potentiometer to adjust the
sensitivity threshold for the DO pin. Turn it slowly while
exposing the sensor to gas (for example from an unlit lighter
held briefly nearby) to calibrate a reasonable trigger point.

Note: MQ2 sensors need a warm-up period of a few minutes after
first power-on for stable readings. Readings taken immediately
after power-on may not be accurate.

Run with:
    python3 mq2_gas_logger.py
Stop with Ctrl+C

Log file:
    gas_log.csv is created in the same folder this script is run from,
    with one row per reading: timestamp, status
"""

from gpiozero import DigitalInputDevice
from datetime import datetime
from time import sleep
import csv
import os

LOG_FILE = "gas_log.csv"
gas_sensor = DigitalInputDevice(17)


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "status"])


def log_reading(status):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(timespec="seconds"), status])


def main():
    ensure_log_file()
    print("Warming up sensor, please wait...")
    sleep(20)
    print("Monitoring started. Logging to", LOG_FILE)

    try:
        while True:
            if gas_sensor.value == 1:
                status = "GAS DETECTED"
            else:
                status = "normal"

            print(datetime.now().isoformat(timespec="seconds"), "-", status)
            log_reading(status)
            sleep(2)
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()
