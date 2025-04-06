import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import socket
import time
from arduino_reader import read_sensors

# Load TensorFlow Lite model
interpreter = tflite.Interpreter(model_path="detect.tflite")
interpreter.allocate_tensors()

# Open socket to send obstacle data
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_IP = "127.0.0.1"
PORT = 5005

def measure_distance():
    """Measures distance using ultrasonic sensor."""
    data = read_sensors()
    return float(data["Distance"])
    
def detect_objects():
    """Detects obstacles using the camera and TensorFlow Lite model."""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()   
    
    if not ret:
        return None

    input_data = cv2.resize(frame, (300, 300))
    input_data = np.expand_dims(input_data, axis=0).astype(np.float32)

    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
    
    return output_data  # Returns detected object data

def check_obstacles():
    """Checks for obstacles and sends an alert if detected."""
    distance = measure_distance()
    objects = detect_objects()
    
    if distance < 50 or objects is not None:
        msg = "OBSTACLE"
        server.sendto(msg.encode(), (SERVER_IP, PORT))

while True:
    check_obstacles()
    time.sleep(0.5)  # Check every 500ms
