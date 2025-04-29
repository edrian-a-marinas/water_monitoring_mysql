import tkinter as tk
from datetime import datetime
from db_connector import insert_data
import socket
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Create TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.4.252', 5000)) #laptop IP  #192.168.4.252(home wifi) #192.168.189.209(mobile hotspot)
server_socket.listen(1)
print("Waiting for connection...")

connection, client_address = server_socket.accept()
print("Connected to", client_address)

print("NOW RUNNING!!! ")


log_entries = []
log_window = None
log_listbox = None
graph_window = None
sensor_data = {'temperature': None, 'water_level': None, 'water_distance': None}

# Graph data storage
graph_times = []
graph_levels = []
level_mapping = {
    'Low': 0,
    'High': 1,
    'Danger': 2
}

def add_to_log(message):
    separator = "-" * 200
    log_entries.insert(0, separator)
    log_entries.insert(0, message)

    if log_listbox is not None and log_listbox.winfo_exists():
        log_listbox.insert(0, separator)
        log_listbox.insert(0, message)
        log_listbox.see(0)
 

def read_socket_data():
    try:
        data = connection.recv(1024).decode('utf-8').strip()  # Receive data from sensor.py
        if data:

            #print(f"Received data: {data}")
            parts = data.split(" ")
            temperature = None
            water_level = None
            water_distance = None

            for part in parts:
                if part.startswith("TEMP:"):
                    temperature = float(part.split(":")[1])
                elif part.startswith("LEVEL:"):
                    raw_level = part.split(":")[1]
                    if "Danger" in raw_level:
                        water_level = "Danger"
                    elif "High" in raw_level:
                        water_level = "High"
                    elif "Low" in raw_level:
                        water_level = "Low"
                    elif "Empty" in raw_level:
                        water_level = "Empty"

                    else:
                        water_level = "Unknown"    
                        
                elif part.startswith("DISTANCE:"):
                    water_distance = float(part.split(":")[1])

            sensor_data['temperature'] = temperature
            sensor_data['water_level'] = water_level
            sensor_data['water_distance'] = water_distance        

            return True
        print(f"didnt Received data from sensor.py")
        return False
        
        
    except Exception as e:
        print("Socket read error:", e)
        return False

def socket_thread():
    while True:
        read_socket_data()

threading.Thread(target=socket_thread, daemon=True).start()


def update_display():   
    if monitoring_active[0]:
        temperature = sensor_data['temperature']
        water_level = sensor_data['water_level']
        water_distance = sensor_data['water_distance']

        if temperature is None or water_level is None:
            print("Sensor read error: Missing data")
            root.after(3000, update_display)  # Try again in 3 seconds
            return

        water_level_label.config(text=f"Water Level: {water_level}")
        temperature_label.config(text=f"Temperature: {temperature} °C")

        timestamp = datetime.now().strftime("%I:%M:%S %p")
        log_msg = f"[{timestamp}] || Water Level: {water_level} --- Temperature: {temperature} °C"

        warnings = []

        if water_distance > 0.1 and water_distance <= 3.00:  
            warnings.append("Water DANGER Level")

        #elif water_distance > 3 and water_distance <= 4.00:  
            #warnings.append("Water High Level")

        if temperature > 40.0:
            warnings.append("HOT Temperature")

        elif temperature < 17.0:
            warnings.append("COLD Temperature")

        if warnings:
            log_msg += " --- WARNING: " + " --and-- ".join(warnings)

        insert_data(water_level, water_distance, temperature, warnings) 
        add_to_log(log_msg)

        # Update Graph data
        # Update Graph data
        now = datetime.now()
        if water_level in level_mapping:
            graph_times.append(now)
            graph_levels.append(level_mapping[water_level])
        else:  # If Unknown or Empty
            graph_times.append(now)
            graph_levels.append(-1)  # special flag for red dot at Low position

        if len(graph_times) > 20:
            graph_times.pop(0)
            graph_levels.pop(0)

        root.after(2500, update_display)  # Schedule the next update in 2.5 seconds 

def toggle_monitoring():
    monitoring_active[0] = not monitoring_active[0]
    if monitoring_active[0]:
        start_button.config(text="Stop Monitoring")
        threading.Thread(target=update_display, daemon=True).start()
    else:
        start_button.config(text="Start Monitoring")
        water_level_label.config(text="Water Level: --")
        temperature_label.config(text="Temperature: --")


def close_log_window():
    global log_window, log_listbox
    log_window.destroy()
    log_window = None
    log_listbox = None

def open_log_window():
    global log_window, log_listbox
    if log_window is not None and log_window.winfo_exists():
        return

    log_window = tk.Toplevel(root)
    log_window.title("Logs")
    log_window.geometry("900x400")
    log_window.protocol("WM_DELETE_WINDOW", close_log_window)

    log_listbox = tk.Listbox(log_window, font=("Arial", 12), width=100, height=20)
    log_listbox.pack(pady=10)

    for entry in log_entries:
        log_listbox.insert(tk.END, entry)

def open_graph_window():
    global graph_window, canvas, fig, ax
    if graph_window is not None and graph_window.winfo_exists():
        return

    graph_window = tk.Toplevel(root)
    graph_window.title("Water Level Graph")

    fig, ax = plt.subplots(figsize=(8, 4))
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    def update_graph():
        ax.clear()

        # Separate normal and unknown/empty data points
        normal_times = []
        normal_levels = []
        error_times = []

        for i, level in enumerate(graph_levels):
            if level != -1:
                normal_times.append(graph_times[i])
                normal_levels.append(level)
            else:
                error_times.append(graph_times[i])

        # Plot normal data
        if normal_times:
            ax.plot(normal_times, normal_levels, marker='o', linestyle='-', color='blue', label='Normal')

        # Plot error data
        if error_times:
            ax.scatter(error_times, [0]*len(error_times), color='red', s=80, label='Unknown/Empty')

        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['Low', 'High', 'Danger'])
        ax.set_xlabel("Time")
        ax.set_ylabel("Water Level")
        ax.set_title("Water Level Over Time")
        ax.grid(True)

        # Match x-axis time format to 2.5s update
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        ax.legend()
        fig.autofmt_xdate(rotation=45)
        canvas.draw()

        graph_window.after(2500, update_graph)

    update_graph()


root = tk.Tk()
root.title("Water Tank Level Monitor")
root.geometry("450x300") #Y and X = left-right and up-down #from x300

monitoring_active = [False]

water_level_label = tk.Label(root, text="Water Level: --", font=("Arial", 16), width=30)
water_level_label.pack(pady=10)

temperature_label = tk.Label(root, text="Temperature: --", font=("Arial", 16), width=30)
temperature_label.pack(pady=10)

start_button = tk.Button(root, text="Start Monitoring", font=("Arial", 14), command=toggle_monitoring)
start_button.pack(pady=10)

log_button = tk.Button(root, text="View Logs", font=("Arial", 12), command=open_log_window)
log_button.pack(pady=5)

graph_button = tk.Button(root, text="View Graph", font=("Arial", 12), command=open_graph_window)
graph_button.pack(pady=5)

root.mainloop()
