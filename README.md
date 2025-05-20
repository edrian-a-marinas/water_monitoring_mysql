Water Monitoring Project

This project is a simple water monitoring system designed to track both the water level and the temperature of a water tank. It uses sensors connected to a Raspberry Pi Pico W to collect data and send it to a laptop or server via TCP/IP. The system continuously monitors the water level, categorizing it into "Danger Level," "High Level," "Low Water," and "Empty," while also monitoring the water temperature.
The collected data is displayed in real-time on a graphical user interface (GUI), graphed, and logged. When certain conditions, such as high temperatures or dangerous water levels, are met, the system logs the sensor data along with corresponding warnings. The system also graphs the data with the same update interval (every 2.5 seconds). If the water level is categorized as "Empty" or "Unknown," a red dot will appear at the bottom of the graph.
All data, including warnings, is stored in a MySQL database for future reference. Communication between the sensors and the server is handled via TCP/IP.
When monitoring is stopped via the GUI, the system halts all data collection, graphing, logging, and database updates. This effectively stops the monitoring process and prevents further data from being recorded or displayed until monitoring is resumed.


Technologies Used:

Programming Language: Python

Hardware: Rasberry Pi Pico w(with Wi-Fi, Bluetooth), Ultrasonic Sensor (HC-SR04), Temperature Sensor (DS18B20).

Library / Module: tkinter, matplotlib, mysql.connector, machine, onewire, ds18x20, network, socket, time, datetime, threading,

Database: mySQL, Xampp, http://localhost/phpmyadmin/

Softwares: Xampp, Git Bash, VSCode, Thonny, cmd.


Note: In the main.py and sensors.py files, you should adjust the functions categorize_water_level, read_distance, and read_temperature depending on the specific setup or hardware you're using, as these functions may need to be modified to suit your environment or sensor configuration.

Note: This is a simple system developed for a school project. However, I have some suggestions for possible upgrades: automated water shutoff when a danger level is detected, automatic water refill when the level is low, automatic water heating when the temperature is too cold, automatic cooling when it's too hot, and other potential features.
