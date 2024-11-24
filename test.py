import cv2

gst_pipeline="nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM),format=NV12,width=1280,height=720,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1"
cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture(0)  # or specify a file/URL
if not cap.isOpened():
    print("Cannot open video source")

