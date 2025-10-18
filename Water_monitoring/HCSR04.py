import machine
import time
import picoData

#HCSR04
# ---------------------------#
# -------- Initialize -------#
# ---------------------------#

TRIG_PIN = 0
ECHO_PIN = 1

def init():
    time.sleep(1)
    trigger = machine.Pin(TRIG_PIN, machine.Pin.OUT)
    echo = machine.Pin(ECHO_PIN, machine.Pin.IN)
    return trigger, echo



# ---------------------------#
# -------- Core Logic -------#
# ---------------------------#

def read_data(sensor):
    trigger, echo = sensor
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
                    return -1
            pulse_start = time.ticks_us()

            while echo.value() == 1:
                if time.ticks_diff(time.ticks_us(), pulse_start) > timeout:
                    return -1
            pulse_end = time.ticks_us()

            pulse_duration = time.ticks_diff(pulse_end, pulse_start)
            distance = (pulse_duration * 0.0343) / 2  # cm
            distance = round(distance, 3)

            if distance > 125:  # ignore invalid readings
                k -= 1
                continue

            dist_add += distance
            time.sleep(0.01)

        except Exception:
            pass

    if (x + 1 - k) == 0:
        return -1

    avg_dist = dist_add / (x + 1 - k)
    dist = round(avg_dist, 3)
    return "distance", dist



# ---------------------------#
# ------- FOR TESTING -------#
# ---------------------------#

def scan():
    try:
        # quick test pulse to verify sensor presence
        trigger = machine.Pin(TRIG_PIN, machine.Pin.OUT)
        echo = machine.Pin(ECHO_PIN, machine.Pin.IN)
        trigger.low()
        time.sleep_ms(10)
        trigger.high()
        trigger.low()
        return True
    except Exception:
        return False


def printDevices(hcsr04_devices):
    print("HCSR04 devices:", "['Detected']" if hcsr04_devices else "None")
    time.sleep(0.1)


if __name__ == '__main__':
    hcsr04_devices = scan()
    printDevices(hcsr04_devices)
    hcsr = init()

    while True:
        data = picoData.HCSR04_OUTPUT(hcsr)
        print(data)
        time.sleep(2)
