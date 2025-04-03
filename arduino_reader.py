import serial
import logging
arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # Change to your port

def read_sensors():
    try:
        data = arduino.readline().decode('utf-8').strip()
        mq135, mq2, distance = map(int, data.split(","))
        return {"MQ135": mq135, "MQ2": mq2, "Distance": distance}
    except Exception as e:
        logging.error(str(e), exc_info=True)
        return None
