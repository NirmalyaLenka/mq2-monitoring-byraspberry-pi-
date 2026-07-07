# MQ2 Gas Sensor Notes
 
The MQ2 is a low-cost gas sensor module commonly used to detect LPG, propane, methane, smoke, alcohol vapor, and other combustible gases. It is a popular beginner choice for simple gas leak or smoke alarm projects.
 
## Pins
 
Most MQ2 modules have four pins:
 
| Pin | Purpose |
|---|---|
| VCC | Power, typically 5V |
| GND | Ground |
| DO | Digital output, HIGH or LOW based on a threshold set by the onboard potentiometer |
| AO | Analog output, a graded voltage that increases with gas concentration |
 
Some breakout boards omit the AO pin and only expose DO. Check your specific module before wiring.
 
## Warm-Up Time
 
MQ2 sensors use a small heating element inside to react to gases, and need a warm-up period after power-on before readings stabilize. A few minutes is typical. All example scripts in this repository include a warm-up delay before logging begins, but for critical use cases, longer warm-up periods (some references suggest 24 to 48 hours for the very first use of a brand new sensor) give more stable long-term readings.
 
## Calibration
 
- The DO threshold is adjusted using the small potentiometer on the module. Turning it changes the sensitivity of the on/off trigger point.
- The AO reading is a raw analog value, not a calibrated ppm (parts per million) reading. Getting an actual ppm value requires calibration against a known, controlled gas concentration and applying the sensor's datasheet response curve, which is beyond a basic beginner setup.
- For simple leak/smoke detection projects (turn on an alarm if gas is detected), the DO pin is usually sufficient and much simpler to work with.
## Safety Notice
 
This sensor and these example scripts are intended for learning and hobby projects. They are not a substitute for a certified, commercially rated gas or smoke detector in any situation where safety is a real concern. Do not rely on a DIY MQ2 setup as your only protection against a genuine gas leak or fire risk.
 
## Example Scripts in This Repository
 
| File | What it does |
|---|---|
| `examples/mq2_gas_logger.py` | Reads the DO pin and logs each reading with a timestamp to `gas_log.csv` |
| `examples/mq2_gas_analog_mcp3008.py` | Reads the AO pin through an MCP3008 ADC and logs raw values and voltage to `gas_analog_log.csv` |
| `examples/mq2_wireless_monitor.py` | Same DO-based monitoring, plus a live web page and JSON API so you can check gas status from any device on your Wi-Fi network |
