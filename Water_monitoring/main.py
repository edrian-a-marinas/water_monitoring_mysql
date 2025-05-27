import tkinter as tk
from datetime import datetime
from db_connector import insert_data
import socket
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000)) #if laptop wifi  #192.168.4.252, if ed wifi #0.0.0.0(Ed hotspot)
server_socket.listen(1)
print("Waiting for connection...")

connection, client_address = server_socket.accept()
print("Connected to", client_address)

print("NOW RUNNING!!! ")


log_entries = []
sensor_data = {'temperature': None, 'water_level': None, 'water_distance': None}
graph_times = []
graph_levels = []
graph_temps = []

level_mapping = {'Low': 0, 'High': 1, 'Danger': 2}
temp_mapping = {'Cold': 0, 'Normal': 1, 'Hot': 2}

monitoring_active = [False]
view_active = [False]

# Log handling
def add_to_log(message):
    separator = "-" * 250
    log_entries.insert(0, separator)
    log_entries.insert(0, message)
    if log_listbox.winfo_ismapped():
        log_listbox.delete(0, tk.END)
        for entry in log_entries:
            log_listbox.insert(tk.END, entry)

# Socket reading
def read_socket_data():
    try:
        data = connection.recv(1024).decode('utf-8').strip()
        if data:
            print(f"Received data: {data}")
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
                    elif "Very" in raw_level:
                        water_level = "Very Low"
                    else:
                        water_level = "Unknown"
                elif part.startswith("DISTANCE:"):
                    water_distance = float(part.split(":")[1])

            sensor_data['temperature'] = temperature
            sensor_data['water_level'] = water_level
            sensor_data['water_distance'] = water_distance
            return True
        return False
    except Exception as e:
        print("Socket read error:", e)
        return False

def socket_thread():
    while True:
        read_socket_data()

threading.Thread(target=socket_thread, daemon=True).start()

# GUI Update
def update_display():
    if monitoring_active[0]:
        temperature = sensor_data['temperature']
        water_level = sensor_data['water_level']
        water_distance = sensor_data['water_distance']

        if temperature is None or water_level is None:
            root.after(2500, update_display)
            return

        water_level_label.config(text=f"Water Level: {water_level}")
        temperature_label.config(text=f"Temperature: {temperature} °C")

        timestamp = datetime.now().strftime("%I:%M:%S %p")
        log_msg = f"[{timestamp}] || Water Level: {water_level} --- Temperature: {temperature} °C"
        warnings = []

        if temperature > 40.0:
            temp_category = 'Hot'
            warnings.append("HOT Temperature")
            graph_temps.append(2)
        elif temperature < 17.0:
            temp_category = 'Cold'
            warnings.append("COLD Temperature")
            graph_temps.append(0)
        else:
            temp_category = 'Normal'
            graph_temps.append(1)

        if water_distance > 0.5 and water_distance <= 7.0:  
            warnings.append("Water DANGER Level")

        insert_data(water_level, water_distance, temperature, warnings)

        if warnings:
            log_msg += " --- WARNING: " + " --and-- ".join(warnings)

        add_to_log(log_msg)

        now = datetime.now()
        graph_times.append(now)

        if water_level in level_mapping:
            graph_levels.append(level_mapping[water_level])
        else:
            graph_levels.append(-1)  # Very Low/Unknown

        if len(graph_times) > 20:
            graph_times.pop(0)
            graph_levels.pop(0)
            graph_temps.pop(0)

        update_graphs()
    root.after(2500, update_display)

# Start/Stop Monitoring
def toggle_monitoring():
    monitoring_active[0] = not monitoring_active[0]
    if monitoring_active[0]:
        start_button.config(text="Stop Monitoring")
        update_display()
    else:
        start_button.config(text="Start Monitoring")
        water_level_label.config(text="Water Level: --")
        temperature_label.config(text="Temperature: --")

# View/Hide Logs and Graphs
def toggle_view():
    view_active[0] = not view_active[0]
    if view_active[0]:
        toggle_view_button.config(text="Stop View Logs and Graphs")
        graphs_frame.pack(side="top", fill="both", expand=True)
        logs_frame.pack(side="bottom", fill="x")
        root.geometry("1200x680")
    else:
        toggle_view_button.config(text="View Logs and Graphs")
        graphs_frame.pack_forget()
        logs_frame.pack_forget()
        root.geometry("450x300")

# Graphs update
def update_graphs():
    ax1.clear()
    ax2.clear()

    normal_times = []
    normal_levels = []
    error_times = []

    for i, level in enumerate(graph_levels):
        if level != -1:
            normal_times.append(graph_times[i])
            normal_levels.append(level)
        else:
            error_times.append(graph_times[i])

    if normal_times:
        ax1.plot(normal_times, normal_levels, marker='o', linestyle='-', color='blue', label='Normal')

    if error_times:
        ax1.scatter(error_times, [0]*len(error_times), color='red', s=80, label='Very Low/Empty')

    ax1.set_yticks([0, 1, 2])
    ax1.set_yticklabels(['Low', 'High', 'Danger'])
    ax1.set_title("Water Level")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax1.grid(True)
    ax1.legend()

    valid_temp_times = graph_times[:len(graph_temps)]
    ax2.plot(valid_temp_times, graph_temps, marker='x', linestyle='-', color='orange', label='Temperature')
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(['Cold', 'Normal', 'Hot'])
    ax2.set_title("Temperature")
    ax2.set_xlabel("Time")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax2.grid(True)
    ax2.legend()

    fig.tight_layout()
    canvas.draw()

root = tk.Tk()
root.title("Water Tank Level Monitor")
root.geometry("450x300")

water_level_label = tk.Label(root, text="Water Level: --", font=("Arial", 16), width=30)
water_level_label.pack(pady=10)

temperature_label = tk.Label(root, text="Temperature: --", font=("Arial", 16), width=30)
temperature_label.pack(pady=10)

start_button = tk.Button(root, text="Start Monitoring", font=("Arial", 14), command=toggle_monitoring)
start_button.pack(pady=10)

toggle_view_button = tk.Button(root, text="View Logs and Graphs", font=("Arial", 12), command=toggle_view)
toggle_view_button.pack(pady=10)

graphs_frame = tk.Frame(root)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 2.8))
canvas = FigureCanvasTkAgg(fig, master=graphs_frame)
canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

logs_frame = tk.Frame(root)
log_listbox = tk.Listbox(logs_frame, font=("Arial", 11), height=8, width=200)
log_listbox.pack(pady=10, padx=5, fill="both", expand=True)

root.mainloop()
