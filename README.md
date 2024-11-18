# Libraries to install on raspberry pi 

Raspian OS:

sudo apt update

sudo apt install libhdf5-dev

sudo apt install libhdf5-serial-dev

sudo apt install libatlas-base-dev

sudo apt install libjasper-dev

sudo apt-get install libqt5gui5 qtbase5-dev

sudo apt install python3-opencv

sudo pip3 install netifaces psutil google-api-python-client wiringpi dronekit opencv-python


To allow app to start automatically on powering raspian
sudo mv droneapp.service /lib/systemd/system/droneapp.service
sudo systemctl daemon-reload
sudo system enable droneapp.service

If you want to stop it from autoloading on Raspi startup, Run:
sudo systemctl disable droneapp.service 

