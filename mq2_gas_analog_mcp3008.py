"""
MQ2 gas/smoke sensor analog reading example, using an MCP3008
analog-to-digital converter, logged to a CSV file.

The MQ2 sensor's AO (analog output) pin gives a much more useful
graded reading than the DO pin's simple on/off threshold, but the
Raspberry Pi has no analog input pins, so an ADC chip is needed.

Wiring (MCP3008 to Pi, using SPI):
    VDD  -> 3.3V
    VREF -> 3.3V
    AGND -> GND
    DGND -> GND
    CLK  -> GPIO11 (SPI SCLK)
    DOUT -> GPIO9  (SPI MISO)
    DIN  -> GPIO10 (SPI MOSI)
    CS   -> GPIO8  (SPI CE0)

MQ2 wiring:
    MQ2 VCC -> 5V
    MQ2 GND -> GND
    MQ2 AO  -> MCP3008 CH0

Enable SPI first with:
    sudo raspi-config
    (Interface Options -> SPI -> Enable)

Install the required library:
    pip3 install adafruit-circuitpython-mcp3xxx

Note: MQ2 sensors need a warm-up period of a few minutes after
first power-on for stable readings, and the raw ADC value is not
a calibrated ppm value, it is only useful for relative comparison
unless you calibrate it against a known gas concentration.

Run with:
    python3 mq2_gas_analog_mcp3008.py
Stop with Ctrl+C

Log file:
    gas_analog_log.csv is created in the same folder, with one row
    per reading: timestamp, raw_value, voltage
"""

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from datetime import datetime
from time import sleep
import csv
import os

LOG_FILE = "gas_analog_log.csv"

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.CE0)
mcp = MCP.MCP3008(spi, cs)
gas_channel = AnalogIn(mcp, MCP.P0)


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "raw_value", "voltage"])


def log_reading(raw_value, voltage):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(timespec="seconds"), raw_value, round(voltage, 3)])


def main():
    ensure_log_file()
    print("Warming up sensor, please wait...")
    sleep(20)
    print("Monitoring started. Logging to", LOG_FILE)

    try:
        while True:
            raw_value = gas_channel.value
            voltage = gas_channel.voltage
            print(datetime.now().isoformat(timespec="seconds"), "- raw:", raw_value, " voltage:", round(voltage, 3))
            log_reading(raw_value, voltage)
            sleep(2)
    except KeyboardInterrupt:
        print("Stopped by user")


if __name__ == "__main__":
    main()
