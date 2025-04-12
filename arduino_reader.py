import serial
import logging

logging.basicConfig(level=logging.INFO)

try:
    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
    logging.info("arduino connected on port ttyACM0")
except serial.SerialException as e:
    logging.error("Serial port error: %s", str(e))
    arduino = None

def read_sensors():
    if not arduino or not arduino.is_open:
        logging.warning("Serial port not available.")
        return None

    try:
        if arduino.in_waiting > 0:  # Check if there's data to read
            data = arduino.readline().decode('utf-8').strip()
            if not data:
                return None

            parts = data.split(",")
            if len(parts) != 3:
                logging.warning("Unexpected data format: %s", data)
                return None

            mq135 = int(parts[0])
            mq2 = int(parts[1])
            distance = float(parts[2])

            return {"MQ135": mq135, "MQ2": mq2, "Distance": distance}
        else:
            # No data in buffer; avoid blocking
            return None

    except (ValueError, serial.SerialException) as e:
        logging.error("Error reading from serial: %s", str(e), exc_info=True)
        return None

