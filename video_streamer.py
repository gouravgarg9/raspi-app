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
import threading

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

logging.info("FPS: %s Quality: %s Width %s Height %s Grayscale: %s", 
             str(FRAMES_PER_SECOND), str(JPEG_QUALITY), str(WIDTH), str(HEIGHT), GRAYSCALE)
logging.info("Drone ID: %s Video Recipient: %s:%s", str(DRONE_ID), str(HOST_IP), str(VIDEO_PORT))

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (WIDTH, HEIGHT)}))
picam2.start()
logging.info("Camera module initiated")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST_IP, VIDEO_PORT))
logging.info("Socket opened, Video Streaming started")

latest_jpeg = None
latest_jpeg_lock = threading.Lock()

time.sleep(2)  # Allow camera to warm up

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        if GRAYSCALE:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        
        # Store for local clients
        with latest_jpeg_lock:
            latest_jpeg = jpg_buffer.tobytes()

        
        datagramMsgBytes = Utils.create_datagram_message(DRONE_ID, jpg_buffer)
        sock.sendall(datagramMsgBytes)
        
except Exception as e:
    logging.error("Video Stream Ended: " + str(e))

finally:
    picam2.stop()
    sock.close()


LOCAL_IP = "127.0.0.1"
LOCAL_PORT = 5006

def local_video_streamer(client_socket):
    logging.info("Local client connected from %s", client_socket.getpeername())
    try:
        while True:
            if 'latest_jpeg' in globals():
                with latest_jpeg_lock:
                    data = latest_jpeg
                    if data is None:
                        continue


                length = len(data)
                client_socket.sendall(length.to_bytes(4, byteorder='big') + data)
                time.sleep(1 / FRAMES_PER_SECOND)
    except Exception as e:
        logging.warning(f"Local client disconnected: {e}")
    finally:
        client_socket.close()

def start_local_tcp_server():
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind((LOCAL_IP, LOCAL_PORT))
    tcp_server.listen(5)
    logging.info(f"Local TCP server started at {LOCAL_IP}:{LOCAL_PORT}")
    
    while True:
        client, _ = tcp_server.accept()
        threading.Thread(target=local_video_streamer, args=(client,), daemon=True).start()
        
tcp_thread = threading.Thread(target=start_local_tcp_server, daemon=True)
tcp_thread.start()