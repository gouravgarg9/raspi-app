# Raspi-App: Onboard UAV Application

## Overview
This repository contains a Python-based application for managing Unmanned Aerial Vehicles (UAVs) on Raspberry Pi. The application integrates several key features to ensure efficient UAV operation, including live video feed transmission, server connectivity, and autonomous behavior in case of disconnection.

## Features
1. **Live Video Feed Transmission:**
   - Streams the UAV's video feed to a remote server using WebSocket.
   - Efficiently processes video frames using OpenCV.
   - TensorFlow Lite is utilized for extracting valuable insights from the feed.

2. **Efficient Protocols and Resource Management:**
   - Uses Google Protocol Buffers (Protobuf) for optimized data serialization and transmission.
   - Employs multiprocessing and multithreading for task management:
     - Separate processes for video streaming and model execution.
     - Dedicated threads for data transmission and reception.

3. **Autonomous Behavior:**
   - Implements a watchdog mechanism to monitor server availability:
     - Freezes the UAV and initiates a Return to Launch (RTL) in case of disconnection.

4. **Control and Communication:**
   - Sends control commands to the Pixhawk flight controller using Dronekit and MAVLink.
   - Easily integrates with simulators, protocols, and UAVs through a modular architecture.

5. **Raspberry Pi Optimization:**
   - Designed for efficient use of onboard computational resources.
   - Provides onboard computational capabilities, reducing server dependency.


## Running in Local:
1. Clone the repository:
```bash
git clone https://github.com/gouravgarg9/raspi-app.git
```

2. Install the modules:
```bash
sudo apt update
sudo apt install libhdf5-dev libhdf5-serial-dev libatlas-base-devl libjasper-dev libqt5gui5 \
qtbase5-dev opencv-contrib-python==4.5.5

sudo apt install -y build-essential cmake git pkg-config libjpeg-dev libtiff-dev libpng-dev \
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev \
libgtk-3-dev libatlas-base-dev gfortran python3-dev

sudo pip install --default-timeout=100 --no-cache-dir netifaces psutil google-api-python-client wiringpi dronekit
```
3. Run the application:
```bash
sudo python3 app.py
```


4. To allow app to start automatically on powering raspian
```bash
sudo mv droneapp.service /lib/systemd/system/droneapp.service
sudo systemctl daemon-reload
sudo system enable droneapp.service
```

5. If you want to stop it from autoloading on Raspi startup, Run:
```bash
sudo systemctl disable droneapp.service
```

