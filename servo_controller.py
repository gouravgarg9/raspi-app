
import time
import threading
import pigpio
import logging

servoPIN = 18  # Works with any GPIO pin on Raspberry Pi

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon")

# Class for servo control
class ServoController(threading.Thread):
    def __init__(self, startAngle):
        threading.Thread.__init__(self)
        self.daemon = True
        self.servoAngle = startAngle
        self.delay_period = 0.01
        self.running = True
        self.setAngle(startAngle)

    def angle_to_pulsewidth(self, angle):
        """
        Convert an angle (0 to 180) to pulse width (500 to 2500 microseconds).
        """
        return int(500 + (angle / 180) * 2000)

    def setAngle(self, angle):
        self.servoAngle = max(0, min(180, angle))  # Clamp angle between 0 and 180

    def run(self):
        while self.running:
            try:
                pulsewidth = self.angle_to_pulsewidth(self.servoAngle)
                pi.set_servo_pulsewidth(servoPIN, pulsewidth)
                time.sleep(self.delay_period)
            except Exception as e:
                logging.error(str(e))
                break

    def stop(self):
        """
        Stop the servo control.
        """
        self.running = False
        pi.set_servo_pulsewidth(servoPIN, 0)  # Turn off servo

 
