# Water Monitoring System

A real-time water monitoring system using a Raspberry Pi Pico W. Tracks water level and temperature via sensors, transmits readings over Wi-Fi using TCP/IP, displays live graphs and logs on a desktop GUI, and stores all data in a MySQL database.

## How It Works

The Pico W reads from two sensors — an HC-SR04 ultrasonic sensor for water level and a DS18B20 for temperature. It connects to Wi-Fi and sends JSON payloads to a PC every 2.5 seconds over TCP/IP.

On the PC, the GUI receives the data, renders live graphs, and logs every reading into MySQL automatically. Data collection continues running in the background even when the graph and log panels are hidden. Clicking **Stop Monitoring** pauses collection and logging.

## Water Level Categories

| Range | Status |
|-------|--------|
| 0.5 – 7.0 cm | Danger |
| 7.1 – 19.5 cm | High |
| 19.6 – 24.9 cm | Low |
| 25 cm and above | Very Low / Empty |

A red dot appears on the graph when water reaches Very Low or Empty.

## Temperature Categories

| Range | Status |
|-------|--------|
| Below 20°C | Cold |
| 20 – 35°C | Normal |
| Above 35°C | Hot |

## Debugging

To see live output in Thonny (Wi-Fi status, sensor readings, JSON payloads), uncomment the `print()` lines in `main.py`, `HCSR04.py`, and `DS18B20.py`. Re-comment them after testing to avoid performance issues during continuous operation.
