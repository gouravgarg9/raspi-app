import cv2
import socket
import logging
import configparser
import argparse
import time
import sys
from utils import Utils

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
        logging.FileHandler(APP_DIR + 'logs/ | ' + str(time.asctime()) + '.log'),
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
camera = cv2.VideoCapture(0)

# Check if the camera was successfully opened
if not camera.isOpened():
    logging.error("Could not open USB camera.")
    sys.exit()

# Set the camera resolution (width and height)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# Set the camera FPS (frames per second)
camera.set(cv2.CAP_PROP_FPS, FRAMES_PER_SECOND)

# Open a socket to send the video stream
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST_IP, VIDEO_PORT))

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
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # If grayscale is enabled, convert the frame to grayscale
        if GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compress the frame to JPEG
        code, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])

        # Create a datagram message with the frame and drone ID
        datagramMsgBytes = Utils.create_datagram_message(DRONE_ID, jpg_buffer)

        # Send the message through the socket
        sock.sendall(datagramMsgBytes)

        # Optional: Clear the frame buffer (not strictly needed in OpenCV)
        frame = None

except Exception as e:
    logging.error(f"Video Stream Ended: {str(e)}")

finally:
    # Clean up and close resources
    if camera.isOpened():
        camera.release()

    if sock is not None:
        sock.close()

    logging.info("Stream ended and resources released")
