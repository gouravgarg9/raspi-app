# Libraries to install on raspberry pi 

Raspian OS:

sudo apt update

sudo apt install libhdf5-dev

sudo apt install libhdf5-serial-dev

sudo apt install libatlas-base-dev

sudo apt install libjasper-dev

sudo apt-get install libqt5gui5 qtbase5-dev

sudo apt install python3-opencv

sudo apt install -y build-essential cmake git pkg-config libjpeg-dev libtiff-dev libpng-dev \
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev \
libgtk-3-dev libatlas-base-dev gfortran python3-dev

pip config set global.index-url https://pypi.org/simple

pip install --default-timeout=100 --no-cache-dir netifaces psutil google-api-python-client wiringpi dronekit opencv-contrib-python

install jasper and equired dependencies

To allow app to start automatically on powering raspian
sudo mv droneapp.service /lib/systemd/system/droneapp.service
sudo systemctl daemon-reload
sudo system enable droneapp.service

If you want to stop it from autoloading on Raspi startup, Run:
sudo systemctl disable droneapp.service 

