import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import socket
import time
from arduino_reader import read_sensors

# Load TensorFlow Lite model
interpreter = tflite.Interpreter(model_path="detect.tflite")
interpreter.allocate_tensors()

# Setup UDP socket for sending alerts
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_IP = "127.0.0.1"
PORT = 5005

# Setup TCP client to receive video stream
VIDEO_STREAM_IP = "127.0.0.1"
VIDEO_STREAM_PORT = 5006
video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_socket.connect((VIDEO_STREAM_IP, VIDEO_STREAM_PORT))

def read_frame_from_stream():
    """Reads a single JPEG frame from the TCP video stream."""
    # Read 4-byte length prefix
    data_len = video_socket.recv(4)
    if not data_len:
        return None
    frame_size = int.from_bytes(data_len, byteorder='big')

    # Read the full frame
    data = b''
    while len(data) < frame_size:
        more = video_socket.recv(frame_size - len(data))
        if not more:
            return None
        data += more

    # Decode the JPEG to an OpenCV frame
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    return frame

def measure_distance():
    """Measures distance using ultrasonic sensor."""
    data = read_sensors()
    return float(data["Distance"])

def detect_objects(frame):
    """Detects obstacles in the given frame using TensorFlow Lite model."""
    input_data = cv2.resize(frame, (300, 300))
    input_data = np.expand_dims(input_data, axis=0).astype(np.float32)

    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
    return output_data

def check_obstacles():
    """Checks for obstacles and sends alert if detected."""
    distance = measure_distance()
    frame = read_frame_from_stream()

    if frame is None:
        return

    objects = detect_objects(frame)

    # Basic check — customize based on your model output
    if distance < 50 or objects is not None:
        msg = "OBSTACLE"
        server.sendto(msg.encode(), (SERVER_IP, PORT))

while True:
    check_obstacles()
    time.sleep(0.5)  # every 500 ms
