import machine
import onewire, ds18x20
import time
import picoData


#DS18B20
# ---------------------------#
# -------- Initialize -------#
# ---------------------------#

ds_pin = machine.Pin(22)  # OneWire data pin


def init():
    time.sleep(1)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    roms = ds_sensor.scan()
    if not roms:
        print("No DS18B20 devices found!")
        return None
    return (ds_sensor, roms)





# ---------------------------#
# -------- Core Logic -------#
# ---------------------------#

def read_data(sensor):
    try:
        if sensor is None:
            return None

        ds_sensor, roms = sensor

        ds_sensor.convert_temp()
        time.sleep_ms(750)

        for rom in roms:
            temperature = ds_sensor.read_temp(rom)
            if temperature is not None:
                return {
                    "temperature": temperature
                }

        return None

    except Exception as e:
        print("DS18B20 read error:", e)
        return None




# ---------------------------#
# ------- FOR TESTING -------#
# ---------------------------#

def scan():
    test_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    devices = test_sensor.scan()
    return [hex(x[0]) for x in devices] if devices else None


def printDevices(ds18b20_devices):
    print("DS18B20 OneWire devices:", ds18b20_devices or "None")
    time.sleep(0.1)


if __name__ == '__main__':
    ds18b20_devices = scan()
    printDevices(ds18b20_devices)
    ds = init()

    while True:
      data = picoData.DS18B20_OUTPUT(ds)
      print(data)      
      time.sleep(2)
