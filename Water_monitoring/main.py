import tkinter as tk
from datetime import datetime
from db_connector import insert_data
import socket
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import time
import json

log_entries = []
sensor_data = {'temperature': None, 'water_level': None, 'water_distance': None}
graph_times = []
graph_levels = []
graph_temps = []
connection = None
connection_established = False

level_mapping = {'Low': 0, 'High': 1, 'Danger': 2}
temp_mapping = {'Cold': 0, 'Normal': 1, 'Hot': 2}

monitoring_active = [False]
view_active = [False]


def wait_for_connection():
    global connection, connection_established
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Listen on all interfaces, port 5000 (must match picoData.py SERVER_ADDRESS port)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(1)
    update_status_label("Waiting for connection...")
    print("Waiting for connection...")

    try:
        connection, client_address = server_socket.accept()
        # optional timeout; keep short so reads don't block forever
        connection.settimeout(5)
        connection_established = True
        update_status_label(f"Connected to {client_address}")
        print("Connected to", client_address)
        # start reader thread
        threading.Thread(target=socket_thread, daemon=True).start()
    except Exception as e:
        print("Socket accept error:", e)
        update_status_label("Connection error")


def read_socket_data():
    global connection, connection_established
    if connection is None:
        return False
    try:
        # Pico sends JSON string; read a bit more bytes to be safe
        data = connection.recv(1024)
        if not data:
            # empty: client disconnected
            print("Received empty data. Client might have disconnected.")
            connection.close()
            connection = None
            connection_established = False
            update_status_label("Client disconnected")
            return False
        text = data.decode('utf-8').strip()
        if not text:
            return False
        return data_received(text)
    except socket.timeout:
        # no data this cycle — still okay, not fatal
        return True
    except Exception as e:
        print("Socket read error:", e)
        try:
            if connection:
                connection.close()
        except Exception:
            pass
        connection = None
        connection_established = False
        update_status_label("Connection lost")
        return False


def socket_thread():
    while True:
        alive = read_socket_data()
        if not alive:
            # pause before trying to read again
            time.sleep(1)
        else:
            time.sleep(0.1)


def add_to_log(message):
    separator = "-" * 250
    log_entries.insert(0, separator)
    log_entries.insert(0, message)
    if log_listbox.winfo_ismapped():
        log_listbox.delete(0, tk.END)
        for entry in log_entries:
            log_listbox.insert(tk.END, entry)


def data_received(data):
    """
    Parse incoming data (expected JSON) and update global sensor_data.
    Returns True if parsing/processing succeeded (client alive), False otherwise.
    """
    global sensor_data

    print(f"Received data: {data}")

    try:
        obj = json.loads(data)
    except Exception as e:
        print("Failed to parse JSON:", e)
        return False

    # defaults
    temperature = None
    water_distance = None
    water_level = None

    # temperature could be numeric or string
    if 'temperature' in obj:
        try:
            temperature = float(obj['temperature'])
        except Exception:
            try:
                temperature = float(str(obj['temperature']).strip())
            except Exception:
                temperature = None

    # water distance may be provided under "water_distance_in_CM" or "water_distance"
    if 'water_distance_in_CM' in obj:
        try:
            water_distance = float(obj['water_distance_in_CM'])
        except Exception:
            try:
                water_distance = float(str(obj['water_distance_in_CM']).strip())
            except Exception:
                water_distance = None
    elif 'water_distance' in obj:
        try:
            water_distance = float(obj['water_distance'])
        except Exception:
            try:
                water_distance = float(str(obj['water_distance']).strip())
            except Exception:
                water_distance = None

    # water level status mapping
    if 'water_level_status' in obj:
        raw_level = obj['water_level_status']
        if not isinstance(raw_level, str):
            raw_level = str(raw_level)
        raw_level = raw_level.strip()

        # Normalize to a small set used in GUI
        if "Danger" in raw_level:
            water_level = "Danger"
        elif "High" in raw_level:
            water_level = "High"
        elif "Low" in raw_level and "Very" not in raw_level:
            water_level = "Low"
        elif "Very" in raw_level:
            water_level = "Low"  # treat "Very Low" as Low for plotting; keep text if you want "Very Low"
        else:
            # fallback to the raw string (trimmed)
            water_level = raw_level

    # Also accept if key names differ slightly
    if 'water_level' in obj and water_level is None:
        w = obj['water_level']
        water_level = w if isinstance(w, str) else str(w)

    # Update globals if we have parsed anything useful
    updated = False
    if temperature is not None:
        sensor_data['temperature'] = temperature
        updated = True
    if water_distance is not None:
        sensor_data['water_distance'] = water_distance
        updated = True
    if water_level is not None:
        sensor_data['water_level'] = water_level
        updated = True

    # If nothing useful parsed, consider it a failed read
    if not updated:
        print("No usable fields parsed from JSON.")
        return False

    # success
    return True


def update_display():
    if monitoring_active[0] and connection_established:
        temperature = sensor_data['temperature']
        water_level = sensor_data['water_level']
        water_distance = sensor_data['water_distance']

        if temperature is None or water_level is None:
            root.after(2500, update_display)
            return

        display_config(temperature, water_level, water_distance)
    root.after(2500, update_display)


def display_config(temperature, water_level, water_distance):
    water_level_label.config(text=f"Water Level: {water_level}")
    temperature_label.config(text=f"Temperature: {temperature} °C")

    timestamp = datetime.now().strftime("%I:%M:%S %p")
    log_msg = f"[{timestamp}] || Water Level: {water_level} --- Temperature: {temperature} °C"
    warnings = []

    # temperature thresholds
    if temperature is not None:
        if temperature > 35.0:
            warnings.append("HOT Temperature")
            graph_temps.append(2)
        elif temperature < 20.0:
            warnings.append("COLD Temperature")
            graph_temps.append(0)
        else:
            graph_temps.append(1)
    else:
        graph_temps.append(1)

    # water danger threshold (matching pico categorize logic)
    if water_distance is not None and 0.5 < water_distance <= 7.0:
        warnings.append("Water DANGER Level")

    # save to DB (your insert_data function should handle types)
    try:
        insert_data(water_level, water_distance, temperature, warnings)
    except Exception as e:
        print("DB insert error:", e)

    if warnings:
        log_msg += " --- WARNING: " + " --and-- ".join(warnings)

    add_to_log(log_msg)

    now = datetime.now()
    graph_times.append(now)

    if water_level in level_mapping:
        graph_levels.append(level_mapping[water_level])
    else:
        # unknown level
        graph_levels.append(-1)

    # keep only last 20
    if len(graph_times) > 20:
        graph_times.pop(0)
        graph_levels.pop(0)
        graph_temps.pop(0)

    update_graphs()


def toggle_monitoring():
    monitoring_active[0] = not monitoring_active[0]
    if monitoring_active[0]:
        if not connection_established:
            update_status_label("Waiting for connection... Cannot monitor yet.")
        else:
            update_status_label("Monitoring started.")
        start_button.config(text="Stop Monitoring")
    else:
        start_button.config(text="Start Monitoring")
        update_status_label("Monitoring stopped.")
        water_level_label.config(text="Water Level: --")
        temperature_label.config(text="Temperature: --")


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
        ax1.plot(normal_times, normal_levels, marker='o', linestyle='-')
    if error_times:
        ax1.scatter(error_times, [0] * len(error_times), s=80)

    ax1.set_yticks([0, 1, 2])
    ax1.set_yticklabels(['Low', 'High', 'Danger'])
    ax1.set_title("Water Level")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax1.grid(True)

    valid_temp_times = graph_times[:len(graph_temps)]
    if valid_temp_times:
        ax2.plot(valid_temp_times, graph_temps, marker='x', linestyle='-')
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(['Cold', 'Normal', 'Hot'])
    ax2.set_title("Temperature")
    ax2.set_xlabel("Time")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax2.grid(True)

    fig.tight_layout()
    canvas.draw()


def update_status_label(text):
    # called from background thread sometimes; try/except to avoid Tkinter thread errors
    try:
        status_label.config(text=f"Status: {text}")
    except Exception:
        pass


# --- GUI Layout ---
root = tk.Tk()
root.title("Water Tank Level Monitor")
root.geometry("450x320")

status_label = tk.Label(root, text="Status: Initializing...", font=("Arial", 11))
status_label.pack(pady=(5, 0))

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


def main():
    threading.Thread(target=wait_for_connection, daemon=True).start()
    update_display()
    root.mainloop()


if __name__ == "__main__":
    main()
