💧 Water Monitoring System — Setup & Usage Guide

This project is a real-time water monitoring system using a Raspberry Pi Pico W and Python (Tkinter + MySQL).
It tracks both water level and temperature, transmits data via TCP/IP, and displays everything on a desktop GUI with live graphs and logs.

⚙️ Project Overview

Raspberry Pi Pico W reads data from:

HCSR04 ultrasonic sensor → water level

DS18B20 temperature sensor → water temperature

The Pico sends the readings via Wi-Fi to your PC/server.

The Desktop GUI displays the readings, graphs, and logs in real time.

All readings are stored in a MySQL database for analysis.

📂 File Structure
File	Location	Description
main.py	Raspberry Pi Pico	Main controller that connects Wi-Fi, reads sensor data, and sends JSON data to the PC
HCSR04.py	Raspberry Pi Pico	Module for the HCSR04 ultrasonic sensor
DS18B20.py	Raspberry Pi Pico	Module for the DS18B20 temperature sensor
RUN_in_Desktop.py	PC / Laptop	GUI program that receives data, displays graphs/logs, and stores them in MySQL
setup_db.py	PC / Laptop	Initializes the MySQL database and creates required tables
db_connector.py	PC / Laptop	Handles data insertion into the MySQL database

🧠 Note:
The files main.py, HCSR04.py, and DS18B20.py must be uploaded to the Raspberry Pi Pico W.
Only RUN_in_Desktop.py, setup_db.py, and db_connector.py should be on your computer.

🪜 Step-by-Step Guide
1️⃣ Setup MySQL Database

Before running the GUI, make sure MySQL is installed and running.

# Run this in your terminal or command prompt
python setup_db.py


✅ This will automatically:

Create a database named water_monitor

Create a table named tbl_water_and_temp

2️⃣ Configure the Pico (Wi-Fi and Server IP)

Edit the following section in main.py before uploading to the Pico:

SSID = 'YourWiFiName'        # Replace with your Wi-Fi name
PASSWORD = 'YourWiFiPassword'
SERVER_ADDRESS = ('192.168.X.XXX', 5000)  # Replace with your computer's local IP address


To find your computer’s IP address, run in Command Prompt:

ipconfig   # (Windows)


or in Terminal:

hostname -I   # (Linux / Mac)


Use the IP address under your Wi-Fi adapter (e.g., 192.168.1.101).

3️⃣ Upload Code to Raspberry Pi Pico

Upload the following three files to your Pico W:

main.py
HCSR04.py
DS18B20.py


You can upload them using Thonny IDE.

When powered via charger or power bank, the Pico will automatically run main.py and start sending data.

4️⃣ Run the Desktop GUI

On your computer, simply run:

python RUN_in_Desktop.py


✅ This will:

Start the GUI

Wait for the Pico to connect

Display real-time data and graphs

Automatically log data into the MySQL database

💡 Tip: The GUI continues collecting data even when the graph and logs are hidden.

5️⃣ Powering the Pico

If the Pico is connected to a laptop, it can be manually run from Thonny.

If connected to a power bank, it automatically runs main.py when powered — no PC required.
The data will still be sent to your laptop’s IP (as long as both are on the same Wi-Fi network).

🧠 Extra Notes

Update Interval: Data updates every 2.5 seconds.

Water Level Categories:

0.5–7.0 cm → Danger Level

7.1–19.5 cm → High Level

19.6–24.9 cm → Low Level

≥25 cm → Very Low / Empty

Temperature Categories:

<20°C → Cold

20–35°C → Normal

35°C → Hot

Critical Alerts: A red dot appears in the graph when water is Very Low or Empty.

🧩 Example Workflow

Power the Pico (connected to sensors).

The Pico connects to Wi-Fi and sends sensor data via TCP/IP.

RUN_in_Desktop.py receives and displays the data.

Logs and graphs update in real time.

Data is saved automatically to MySQL.

When you click Stop Monitoring, data collection and logging pause.

🖼️ Preview (Optional)

You can add a screenshot of your GUI here later, for example:

![Water Monitoring GUI](screenshot.png)

📚 Technologies Used

Python (Tkinter, Matplotlib, MySQL Connector)

Raspberry Pi Pico W (MicroPython)

DS18B20 Temperature Sensor

HCSR04 Ultrasonic Sensor

MySQL Database

TCP/IP Communication