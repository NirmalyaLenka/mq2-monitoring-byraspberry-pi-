# MQ-2 Gas Sensor Monitoring on Raspberry Pi

A small Python learning project for reading an MQ-2 gas-sensor module from a Raspberry Pi. The repository contains three independent scripts: a digital-output CSV logger, an MCP3008 analog logger, and a local-network status page.

> **Safety:** This is a hobby prototype, not a certified gas or smoke alarm. Do not use it as the only protection against gas leaks or fire. Keep a certified detector installed and follow the sensor/module manufacturer's electrical guidance.

## Repository contents

| File | Purpose | Hardware/interface |
|---|---|---|
| `mq2_gas_logger.py` | Logs the digital sensor state with timestamps to `gas_log.csv` | MQ-2 DO → BCM GPIO17 |
| `mq2_gas_analog_mcp3008.py` | Logs raw ADC counts and measured voltage to `gas_analog_log.csv` | MQ-2 AO → MCP3008 CH0; SPI |
| `mq2_wireless_monitor.py` | Logs digital state and serves a small status page plus JSON endpoint | MQ-2 DO → BCM GPIO17; Flask on port 5000 |

All files are in the repository root; there is no `examples/` directory, `requirements.txt`, or automated test suite in the current tree.

## How the scripts behave

- The digital scripts sample every 2 seconds after a 20-second startup delay.
- The analog script reads MCP3008 channel 0 and records the ADC raw value and voltage. These values are **not calibrated ppm measurements**.
- The wireless monitor serves `/` and `/api/reading` on port `5000`. The API returns the latest status and timestamp as JSON. The server binds to `0.0.0.0`, making it reachable from other devices on the network.
- Run one script at a time. The two digital scripts share the filename `gas_log.csv`; running both together can produce overlapping records.

## Hardware and wiring

### Digital-output scripts

| MQ-2 module pin | Connection |
|---|---|
| VCC | Module-rated supply; many boards use 5 V |
| GND | Raspberry Pi ground (common ground) |
| DO | BCM GPIO17, only if the module's digital output is 3.3 V compatible |

**Raspberry Pi GPIO is not 5 V tolerant.** Before connecting DO, verify the output voltage of your specific breakout. Use an appropriate logic-level shifter or interface if it can output more than 3.3 V. Do not connect a 5 V logic signal directly to GPIO17.

### Analog script with MCP3008

The Raspberry Pi has no built-in analog input, so this script uses an MCP3008 over SPI.

| MCP3008 pin/signal | Raspberry Pi connection |
|---|---|
| VDD, VREF | 3.3 V |
| AGND, DGND | GND |
| CLK | BCM GPIO11 / SPI SCLK |
| DOUT | BCM GPIO9 / SPI MISO |
| DIN | BCM GPIO10 / SPI MOSI |
| CS | BCM GPIO8 / SPI CE0 |
| CH0 | MQ-2 AO, **only after checking and limiting the signal voltage** |

The MQ-2 module is commonly powered from 5 V, and its AO output may exceed the MCP3008's 3.3 V reference. **Do not connect AO directly until you have verified the maximum output voltage.** Add a correctly sized voltage divider or suitable level-conditioning circuit so the ADC input never exceeds VREF (3.3 V in this wiring). Check the MCP3008 and sensor-module datasheets for your exact boards.

Enable SPI through `sudo raspi-config` → **Interface Options** → **SPI** before using the analog script.

## Setup

These commands target Raspberry Pi OS. Run them from the repository root.

```bash
sudo apt update
sudo apt install -y python3-venv python3-gpiozero
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install flask adafruit-blinka adafruit-circuitpython-mcp3xxx
```

The digital logger needs GPIO Zero and Raspberry Pi GPIO support. The analog logger additionally needs Blinka and the MCP3008 CircuitPython library. The wireless monitor additionally needs Flask. If you only use one script, you can install only the dependencies it needs.

## Run

From the repository root, choose one script:

```bash
source .venv/bin/activate
python mq2_gas_logger.py
```

Or run the analog logger after wiring the MCP3008 and enabling SPI:

```bash
python mq2_gas_analog_mcp3008.py
```

Or start the wireless monitor:

```bash
python mq2_wireless_monitor.py
```

Find the Pi's LAN address with `hostname -I`, then open `http://<pi-ip-address>:5000/` from a device on the same trusted network. The JSON endpoint is `http://<pi-ip-address>:5000/api/reading`. Stop a script with **Ctrl+C**.

The scripts create CSV files in the **current working directory**. Run them from the repository root if you want the logs there. Review generated CSV files before committing; they are runtime data, not source files.

## Warm-up, calibration, and interpretation

- The scripts wait 20 seconds before starting their loops. This delay is not a calibration procedure and may be insufficient for stable readings; follow the module/datasheet warm-up guidance and allow longer stabilization where appropriate.
- The onboard potentiometer adjusts the digital-output threshold. Verify the output polarity and threshold behavior for your specific module.
- Analog readings are raw ADC counts/voltage, not calibrated ppm. Meaningful concentration estimates require appropriate calibration with known gas concentrations and the sensor's documented response characteristics.
- Sensor response varies with warm-up, environment, and the gases present. Do not interpret a simple `normal` status as proof that the air is safe.

## Troubleshooting

- **GPIO permission/backend errors:** Confirm GPIO Zero and the supported Raspberry Pi GPIO backend are installed for your OS; run on the Pi rather than an ordinary desktop.
- **No analog readings:** Enable SPI, recheck MCP3008 pin orientation and channel 0, and verify the input voltage is within the ADC's permitted range.
- **Unexpected digital state:** Check the module's DO polarity and potentiometer threshold; do not assume every breakout has identical logic behavior.
- **Cannot open the web page:** Confirm the script is running, use the Pi's current LAN IP, and check local firewall/network isolation settings.
- **CSV appears in another directory:** The path is relative to the directory from which Python was launched.

## Network and safety limitations

The Flask development server has no authentication and listens on all network interfaces. Use it only on a trusted, isolated LAN; do not port-forward it or expose it directly to the internet. It is a simple status display, not a safety-rated alarm service.

## Maintenance & Audit

- **Audit date:** 21 November 2026
- **Documentation status:** README reviewed and audit record added on this date.
- **Scope and evidence:** This is a documentation-level maintenance pass. It does not establish that source code compiles, dependencies are current, security has been tested, or hardware/runtime behavior has been verified.
- **Code and tests:** No new functional code changes or test results are claimed by this README update. Run project-specific build, test, and hardware/runtime checks before relying on the project.
- **Maintenance baseline:** Documentation status recorded through 11 November 2026; revisit setup instructions, dependencies, known limitations, and tests when the project changes.
