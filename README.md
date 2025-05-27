Water Monitoring Project

This project is a simple water monitoring system designed to track both the water level and the temperature of a water tank. It uses sensors connected to a Raspberry Pi Pico W to collect data and send it to a laptop or server via TCP/IP. The system continuously monitors the water level, categorizing it into "Danger Level," "High Level," "Low Water," and "Empty," while also monitoring the water temperature as "Cold," "Normal," or "Hot." The system also calculates and prints the current water height inside the tank by subtracting the measured distance from the total height of the tank (25 cm), and this value is available only on the Raspberry Pi Pico sensor.py side. The collected data is displayed in real-time on a graphical user interface (GUI) and is updated every 2.5 seconds. A toggle button is available to show or hide the logs and graphs, all within the same window. Even when the graphs and logs are hidden, the system continues to update and process data in the background. The GUI includes a red dot marker that appears in the water level graph to indicate when the level is categorized as "Very Low" or "Empty," providing a quick visual alert of critical conditions. Temperature and water level data are graphed using matplotlib, and each data point is logged with a timestamp along with any applicable warnings such as high temperature or dangerous water levels. These logs are stored in a MySQL database for future reference and analysis. The system applies basic data science techniques such as time-series logging, data categorization, and visual trend analysis to help users understand behavior patterns and anomalies over time. Communication between the sensors and the server is handled via TCP/IP, with all data transmitted and processed in real time. When monitoring is stopped through the GUI, the system halts all data collection, logging, graphing, and database updates, effectively pausing the process until resumed by the user.


Technologies Used:

Programming Language: Python

Hardware: Rasberry Pi Pico w(with Wi-Fi, Bluetooth), Ultrasonic Sensor (HC-SR04), Temperature Sensor (DS18B20).

Library / Module: tkinter, matplotlib, mysql.connector, machine, onewire, ds18x20, network, socket, time, datetime, threading,

Database: mySQL, Xampp, http://localhost/phpmyadmin/

Softwares: Xampp, Git Bash, VSCode, Thonny, cmd.


Note: In the main.py and sensors.py files, you should adjust the functions categorize_water_level, read_distance, and read_temperature depending on the specific setup or hardware you're using, as these functions may need to be modified to suit your environment or sensor configuration.

Note: This is a simple system developed for a school project. However, I have some suggestions for possible upgrades: automated water shutoff when a danger level is detected, automatic water refill when the level is low, automatic water heating when the temperature is too cold, automatic cooling when it's too hot, and other potential features.
