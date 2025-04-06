import serial

arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Change to your port

def read_sensors():
	try:
		data = arduino.readline().decode('utf-8').strip()
		mq135_str, mq2_str, distance_str = data.split(",")
		mq135 = int(mq135_str)
		mq2 = int(mq2_str)
		distance = float(distance_str)
		return {"MQ135": mq135, "MQ2": mq2, "Distance": distance}
	except Exception as e:
		logging.error(str(e), exc_info=True)
		return None
