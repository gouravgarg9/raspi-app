import time
import socket
import logging
import configparser
import argparse
import sys
import numpy as np
import cv2
from picamera2 import Picamera2
from utils import Utils
from ultralytics import YOLO

model = YOLO("./best.pt")

parser = argparse.ArgumentParser()
parser.add_argument('-d', nargs=1, default=None)
args = parser.parse_args()

APP_DIR = args.d[0] if args.d else "./"
CONFIGURATIONS = APP_DIR + 'configuration.ini'

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(APP_DIR + 'logs/video-streamer_' + str(int(time.time())) + '.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger("picamera2").setLevel(logging.WARNING)

config = configparser.ConfigParser()
if len(config.read(CONFIGURATIONS)) == 0:
    logging.error("Could Not Read Configurations File: " + CONFIGURATIONS)
    sys.exit()

DRONE_ID = config['drone']['id']
HOST_IP = config['cloud-app']['ip']
VIDEO_PORT = int(config['cloud-app']['video-port'])

GRAYSCALE = config['video']['grayscale'].lower() == 'true'
FRAMES_PER_SECOND = int(config['video']['fps'])
JPEG_QUALITY = int(config['video']['quality'])
WIDTH = int(config['video']['width'])
HEIGHT = int(config['video']['height'])

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (WIDTH, HEIGHT)}))
picam2.start()
logging.info("Camera module initiated")
logging.info("FPS: %s Quality: %s Width %s Height %s Grayscale: %s", str(FRAMES_PER_SECOND), str(JPEG_QUALITY), str(WIDTH), str(HEIGHT), GRAYSCALE)
time.sleep(2)  # Allow camera to warm up

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST_IP, VIDEO_PORT))
logging.info("Drone ID: %s Video Recipient: %s:%s", str(DRONE_ID), str(HOST_IP), str(VIDEO_PORT))
logging.info("Socket opened, Video Streaming started")

def detect_smoke(frame):
    if frame is None:
        return frame

    # YOLO expects RGB images
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run inference
    results = model.predict(source=rgb_frame, conf=0.5, verbose=False)

    # Draw bounding boxes on original frame
    if results and results[0].boxes:
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Draw rectangle (you can customize color based on cls if needed)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Smoke {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    return frame

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = detect_smoke(frame)
        if GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        _, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        
        datagramMsgBytes = Utils.create_datagram_message(DRONE_ID, jpg_buffer)
        sock.sendall(datagramMsgBytes)
        
except Exception as e:
    logging.error("Video Stream Ended: " + str(e))

finally:
    picam2.stop()
    sock.close()

