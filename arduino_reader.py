import serial

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # Change to your port

def read_sensors():
    try:
        data = arduino.readline().decode('utf-8').strip()
        mq135, mq2, distance = map(int, data.split(","))
        return {"MQ135": mq135, "MQ2": mq2, "Distance": distance}
    except:
        return None

if __name__ == "__main__":
    while True:
        sensor_data = read_sensors()
        if sensor_data:
            print(sensor_data)
