import cv2
import socket
import logging
import configparser
import argparse
import time
import sys
import numpy as np
from utils import Utils
from ultralytics import YOLO
model = YOLO("./best.pt")

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

# Command-line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('-d', nargs=1, default=None)
args = parser.parse_args()

APP_DIR = args.d[0] if args.d != None else "./"
CONFIGURATIONS = APP_DIR + 'configuration.ini'

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler( './logs/' + 'a.log'),
        logging.StreamHandler()
    ]
)

# Load configuration
config = configparser.ConfigParser()

if len(config.read(CONFIGURATIONS)) == 0:
    logging.error("Could Not Read Configurations File: " + CONFIGURATIONS)
    sys.exit()

# Extract values from configuration
DRONE_ID = config['drone']['id']
HOST_IP = config['cloud-app']['ip']
VIDEO_PORT = int(config['cloud-app']['video-port'])

GRAYSCALE = config['video']['grayscale'].lower() == 'true'
FRAMES_PER_SECOND = int(config['video']['fps'])
JPEG_QUALITY = int(config['video']['quality'])
WIDTH = int(config['video']['width'])
HEIGHT = int(config['video']['height'])

logging.info("FPS: %s Quality: %s Width %s Height %s Grayscale: %s",
    str(FRAMES_PER_SECOND), str(JPEG_QUALITY), str(WIDTH), str(HEIGHT), GRAYSCALE)
logging.info("Drone ID: %s Video Recipient: %s:%s", str(DRONE_ID), str(HOST_IP), str(VIDEO_PORT))
# OpenCV VideoCapture for USB camera (camera index 0 is usually the default USB camera)
camera = cv2.VideoCapture('./videoplayback.webm')

# gst_pipeline = "v4l2src device=/dev/video0 ! videoconvert ! appsink"
# gst_pipeline = "nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM),format=NV12,width=1280,height=720,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1"
# camera = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

# Check if the camera was successfully opened
if not camera.isOpened():
    logging.error("Could not open USB camera.")
    sys.exit()

# Set the camera resolution (width and height)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# Set the camera FPS (frames per second)
camera.set(cv2.CAP_PROP_FPS, FRAMES_PER_SECOND)

logging.info("Camera module initiated and socket opened, Video Streaming started")

try:
    while True:
        # Read a frame from the camera
        ret, frame = camera.read()

        # Check if the frame was captured successfully
        if not ret:
            logging.error("Failed to capture frame from camera")
            break

        # Rotate the frame 180 degrees (as in original code)
        # frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame = detect_smoke(frame)
        # If grayscale is enabled, convert the frame to grayscale
        if GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow('frame', frame)
                # ADD THIS
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # Compress the frame to JPEG
        code, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])


        # Optional: Clear the frame buffer (not strictly needed in OpenCV)
        frame = None

except Exception as e:
    logging.error(f"Video Stream Ended: {str(e)}")

finally:
    # Clean up and close resources
    if camera.isOpened():
        camera.release()
    logging.info("Stream ended and resources released")
