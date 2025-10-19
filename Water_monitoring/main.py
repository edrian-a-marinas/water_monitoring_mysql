import HCSR04, DS18B20 #import files
import socket, network, time, json

#this main.py should be run too by the pico itself or thonny. then run the RUN_in_Desktop so they will connect to each other

#------------------ Connect Config ----------------------#

SSID = 'Edrian' #Your wifi name   
PASSWORD = 'EdrianPassword' #Your Wifi password
SERVER_ADDRESS = ('192.168.?.???', 5000) # Replace IP Address of your laptop/pc wifi 
wlan = network.WLAN(network.STA_IF)


#------------------ Wifi & device IP ----------------------#

def wifi_Scanning():
    wlan.active(True)

    while True: 
        #print('Connecting to Wi-Fi...')
        networks = wlan.scan()

        if any(net[0].decode() == SSID for net in networks):
            #print(f"Connecting to {SSID} ", end="")
            wlan.connect(SSID, PASSWORD)
            timeout = 15
            while not wlan.isconnected() and timeout > 0:
                print(".", end="")
                time.sleep(1)
                timeout -= 1
            print()
            if wlan.isconnected():
                #print("Connected to WiFi!")
                return True
        time.sleep(5)



def deviceIP_Scanning():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = SERVER_ADDRESS
    while True:
        try:
            #print(f"Connecting to {server_address}...")
            sock.connect(server_address)
            #print("Connected to PC.\n")
            return sock 
        except OSError:
            #print("Connection failed, retrying in 2.5 seconds...")
            time.sleep(2.5)





#------------------ Catergorize ----------------------#

def categorize_water_level(distance):
    if distance == -1:
        pass
    
    elif distance >= 0.5 and distance <= 7.0:  
        return "Danger Level"
    
    elif distance > 7.0 and distance <= 19.5:
        return "High Level"

    elif distance > 19.5 and distance < 25.00:  
        return "Low Level"
    
    else:
        return "Very Low" 






#------------------ JSON Creation ----------------------#

def create_json(hcrData, dsData):
    if not (hcrData and dsData):
        return None

    # HCSR04 returns tuple
    distance = hcrData[1]

    # DS18B20 returns dictionary
    temperature = dsData['temperature']

    water_level_status = categorize_water_level(distance)

    data_dict = {
        "water_distance_in_CM": f"{distance:.2f}",
        "temperature": f"{temperature:.2f}",
        "water_level_status": water_level_status
    }

    json_data = json.dumps(data_dict)
    return json_data





#------------------ Print Data----------------------#

def printData(hcrData, dsData):
    distance = hcrData[1]
    temperature = dsData['temperature']
    
    water_level_status = categorize_water_level(distance)

    print(f"HCSR04        ==>  Distance {distance:.2f} cm")
    print(f"DS18B20       ==>  Temperature: {temperature:.2f}")
    print(f"Water Status  ==>  {water_level_status}")
    





# ------------------ Send Data ---------------------- #

def send_data_to_MainGUI(sock, data):
    try:
        #print(f"sending data: {data}")
        sock.sendall(data.encode())  
    except Exception as e:
        #print(f"Error in sending data: {e}")
        pass

    



#------------------ Sensors Reading ----------------------#

def HCSR04_OUTPUT(hcr):
    data = HCSR04.read_data(hcr)
    return data
        

def DS18B20_OUTPUT(ds):
    data = DS18B20.read_data(ds)
    return data





    
#------------------ Main Loop ----------------------#    

def main():
    if not wifi_Scanning():
        return
    
    
    sock = deviceIP_Scanning()
    
    #print("Stabilizing system... please wait few seconds.")

    hcr = HCSR04.init()
    ds = DS18B20.init()
    
    #print("\n=== SENSOR DATA OUTPUT START ===\n")

    while True:
        hcrData = HCSR04_OUTPUT(hcr)
        dsData = DS18B20_OUTPUT(ds)

        #printData(hcrData, dsData)

        json_payload = create_json(hcrData, dsData)

        if json_payload:  # Only print if it's not None
            #print("JSON Output:", json_payload)
            send_data_to_MainGUI(sock, json_payload)

            pass

        time.sleep(2)

if __name__ == '__main__':          
    main()

