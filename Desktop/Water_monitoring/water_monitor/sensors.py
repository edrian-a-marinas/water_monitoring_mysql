import machine
import onewire, ds18x20
import socket
import network
import time




# Replace with your Wi-Fi credentials
ssid = 'Hisense2G' #wifi name   #Hisense2G #Ed
password = 'hershey2024' #wifi pass #hershey2024 #Edrian27

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)


print('Connecting to Wi-Fi...')
while not wlan.isconnected():
    time.sleep(1)


print('Connected to Wi-Fi')
print('IP address:', wlan.ifconfig()[0])  

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.4.252', 5000)  # Replace IP Address of laptop  #192.168.4.252 (home wifi) , #192.168.189.209 (Phone data hotspot)

print(f"Connecting to {server_address}...")
sock.connect(server_address)
print("Connected to PC.\n")

print("NOW RUNNING !!!!!!!")

ds_pin = machine.Pin(22) 
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()


TRIG_PIN = 0   
ECHO_PIN = 1  
trigger = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)



def read_temperature():
    if not roms:
        return None
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp_c = ds_sensor.read_temp(rom)
        if temp_c is not None:
            return round(temp_c, 2)
    return None

def read_distance():
    k = 0
    dist_add = 0
    for x in range(5):
        try:
            
            trigger.low()
            time.sleep_us(2)
            trigger.high()
            time.sleep_us(10)
            trigger.low()

            start_time = time.ticks_us()
            timeout = 30000  # 30 ms timeout

            while echo.value() == 0:
                if time.ticks_diff(time.ticks_us(), start_time) > timeout:
                    return -1  # Timeout, no object detected
            pulse_start = time.ticks_us()

            while echo.value() == 1:
                if time.ticks_diff(time.ticks_us(), pulse_start) > timeout:
                    return -1  # Timeout
            pulse_end = time.ticks_us()

            pulse_duration = time.ticks_diff(pulse_end, pulse_start)
            distance = (pulse_duration * 0.0343) / 2  # cm
            distance = round(distance, 3)

            if distance > 125:
                k = k - 1
                continue

            dist_add += distance
            time.sleep(0.01)

        except Exception as e:
            pass

    if (x + 1 - k) == 0:
        return -1 

    avg_dist = dist_add / (x + 1 - k)
    dist = round(avg_dist, 3)
    return dist


def categorize_water_level(distance):
    if distance == -1:
        return "Unknown"
    
    elif distance >= 0.2 and distance <= 3.0:  
        return "Danger Level"
    
    elif distance > 3.0 and distance <= 4.00:
        return "High Level"

    elif distance > 4.00 and distance < 6.00:  
        return "Low Water"
    
    else:
        return "Empty" 
    

def send_data_to_pc(temperature, water_level, water_distance):
    try:
        data = f"DISTANCE:{water_distance} TEMP:{temperature} LEVEL:{water_level}\n"
        #print(f"sending data: {data}")
        sock.sendall(data.encode())  
    except Exception as e:
        print(f"Error in sending data: {e}")

def pico_w_run():
    while True:
        temp = read_temperature()
       # print(f"done reading temp")
        water_distance = read_distance()
        #print(f"done distance cm")
        water_level_status = categorize_water_level(water_distance)
        #print(f"done status")
        send_data_to_pc(temp, water_level_status, water_distance)
        #print(f"dont sent to pc")
        

        if temp is not None:
            pass
            #print("temp is not none")       
        
        else:
            print("TEMP: Sensor Error")

        print(f"Distance: {water_distance} cm")
        print(f"LEVEL: {water_level_status}")
 
 
        time.sleep(0.1)    
pico_w_run()


