# Raspi-App: Onboard UAV Application

## Overview
This repository contains a Python-based onboard UAV application for **Raspberry Pi** that handles real-time video streaming, autonomous flight, environmental sensing, and robust server communication. It enables UAVs to function intelligently in both connected and disconnected modes, supporting real-world operations like surveillance, air quality monitoring, and threat detection.

## Key Features

### 1. 📹 Live Video Feed & Inference
- Uses **Picamera v2.1** for high-quality onboard video capture.
- Streams video to a remote server using **WebSocket**.
- Integrates **TensorFlow Lite** for real-time object detection and inference on edge.

### 2. 📦 Efficient Protocols & Resource Optimization
- Implements **Google Protocol Buffers (Protobuf)** for efficient data transmission.
- Utilizes **multiprocessing** and **multithreading**:
  - Separate processes for video capture, inference, and telemetry.
  - Threads manage Bluetooth, serial, and WebSocket communication without blocking each other.

### 3. 🧭 Autonomous UAV Navigation
- Supports **autonomous path planning** within a defined GPS boundary.
- Includes **obstacle avoidance** using ultrasonic sensors.
- Enables **fail-safe RTL (Return to Launch)** if server communication is lost.

### 4. 🌡️ Environmental Sensing via Arduino
- Connected via **`/dev/ttyAMA0`** serial port.
- Sensors included:
  - **MQ-135 & MQ-2** for air quality and gas detection.
  - **DHT11** for temperature and humidity monitoring.
  - **Ultrasonic Sensor** for obstacle avoidance.

### 5. 📊 Dataset Logging
- Automatically logs sensor and GPS data into a `.csv` file:
  - Attributes: `timestamp`, `longitude`, `latitude`, `speed`, `altitude`, `mq-135`, `mq-2`, `temperature`, `humidity`.
- Useful for **training machine learning models**, **research**, and **analytics**.

### 6. 📡 Drone Communication
- Communicates with **Pixhawk** using **DroneKit** and **MAVLink**.
- Fully compatible with simulators and modular for different flight stacks.

### 7. 🧠 Edge Intelligence
- Onboard inference enables decision-making without needing constant server access.
- Supports future expansion to swarming and collaborative UAV missions.

---

## 🛠 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/gouravgarg9/raspi-app.git
cd raspi-app
```
### Step2: Install Dependencies
```bash
sudo apt update

# Core dependencies
sudo apt install -y libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev \
qtbase5-dev libqt5gui5 opencv-contrib-python==4.5.5

# Camera & vision packages
sudo apt install -y build-essential cmake git pkg-config libjpeg-dev libtiff-dev libpng-dev \
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev \
libgtk-3-dev libatlas-base-dev gfortran python3-dev

# Python packages
sudo pip3 install --default-timeout=100 --no-cache-dir \
netifaces psutil google-api-python-client wiringpi dronekit pyserial
```
### Step 3: Enable PiCamera
```bash
sudo raspi-config
# Interface Options > Camera > Enable
```
## 🚀 Running the Application
```bash
sudo python3 app.py
```

## 🔄 Autostart on Boot
### To enable the application to run on Raspberry Pi boot:
```bash
ssudo mv droneapp.service /lib/systemd/system/droneapp.service
sudo systemctl daemon-reload
sudo systemctl enable droneapp.service
```
### To disable autostart:
```bash
sudo systemctl disable droneapp.service
```

## 📂 Related Repository
### Drone Server (Web Interface + Monitoring):
https://github.com/gouravgarg9/drone-server
