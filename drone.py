import time, logging, netifaces
from dronekit import connect, VehicleMode, Command
import ProtoData_pb2 as proto
from control_tab import ControlTab
from arduino_reader import read_sensors
from data_logger import init_logger, log_data

class Drone:
    def __init__(self, configurations):
        drone_id      = configurations['drone']['id']
        use_simulator = configurations['drone']['use-simulator'].lower() == 'true'
        rpi_ip = configurations['drone']['rpi_ip']
        uav_device  = configurations['drone']['uav_device']
        rpi_sim_port      = int( configurations['drone']['rpi_sim_port'])
        takeoff_alt   = int( configurations['drone']['takeoff-alt'])
        rtl_alt       = int( configurations['drone']['rtl-alt'])
        self.logging_data_to_csv = configurations['drone']['logging_data_to_csv'].lower() == 'true'

        if use_simulator:
            self.vehicle = connect(rpi_ip + ":" + str(rpi_sim_port),  baud=57600, wait_ready=True)
            logging.info('Connected to Simulator On Port: %s ', str(rpi_sim_port))
        else:
            self.vehicle = connect(uav_device, wait_ready=True, baud=57600)
            logging.info('Connected to Flight Controller Hardware on:  %s ', uav_device)
            
        self.drone_id = drone_id
        self.takeoff_alt = takeoff_alt
        self.rtl_alt = rtl_alt
        self.state = "DISARMED"
        self.is_active =True
        self.control_tab = ControlTab(self)
        logging.info("Drone connected")
        init_logger()
        

    def getDroneDataSerialized(self):
        drone_data = proto.DroneData()
        sensor_values = read_sensors()
        drone_data.altitude = self.vehicle.location.global_relative_frame.alt or 1
        drone_data.latitude = self.vehicle.location.global_relative_frame.lat or 1
        drone_data.longitude = self.vehicle.location.global_relative_frame.lon or 1
        drone_data.voltage = self.vehicle.battery.voltage or 1
        drone_data.speed = float(self.vehicle.airspeed) or 1
        drone_data.state = self.state
        drone_data.drone_id = str(self.drone_id)
        drone_data.mq135 = sensor_values["MQ135"] or 1
        drone_data.mq2 = sensor_values["MQ2"] or 1
        drone_data.distance = sensor_values["Distance"] or 1
        drone_data.temperature = sensor_values["Temperature"] or 1
        drone_data.humidity = sensor_values["Humidity"] or 1
        if self.logging_data_to_csv :
            log_data(
                drone_data.latitude,
                drone_data.longitude,
                drone_data.speed,
                drone_data.altitude,
                drone_data.mq135,
                drone_data.mq2,
                drone_data.temperature,
                drone_data.humidity,
            )
        return drone_data.SerializeToString()
            
    def freeze(self):
        logging.info('Freezing in a spot')
        self.control_tab.stopMovement()
    
    def return_to_launch(self):
        self.control_tab.goHome(self.rtl_alt)
    
    #def togleLights(self):
        #self.control_tab.togleLights()

    def close(self):
        self.vehicle.close()


    def executeCommand(self, command):
        if command.code == 7:
            self.control_tab.goHome(self.rtl_alt)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Go Home')
            self.state = "HOME"
            return
        if command.code == 8:
            self.togleLights()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Togle Lights / Drop Package')
            return
        if command.code == 9:
            self.state = "ARMING"
            self.control_tab.armAndTakeoff(self.takeoff_alt)
            self.state = "READY"
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Arm And Takeoff')
            return
        if command.code == 1:
            self.control_tab.increaseSpeedZ()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Increase Vertival Speed')
            return
        if command.code == 5:
            self.control_tab.decreaseSpeedZ()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Decrease Vertival Speed')
            return
        if command.code == 2:
            self.control_tab.rotateLeft(10)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Rotate Left 10 Deg')
            return
        if command.code == 3:
            self.control_tab.rotateRight(10)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Rotate Right 10 Deg')
            return
        if command.code == 18:
            self.control_tab.rotateLeft(45)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Rotate Left 45 Deg')
            return
        if command.code == 19:
            self.control_tab.rotateLeft(90)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Rotate Left 90 Deg')
            return
        if command.code == 20:
            self.control_tab.rotateRight(45)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Rotate Right 45 Deg')
            return
        if command.code == 21:
            self.control_tab.rotateRight(90)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Rotate Right 90 Deg')
            return
        if command.code == 22:
            self.control_tab.cameraUP()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Move Camera Up')
            return
        if command.code == 23:
            self.control_tab.cameraDOWN()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Move Camera Down')
            return
        if command.code == 10:
            self.control_tab.land()
            self.state = "LAND"
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Landing')
            return
        if command.code == 11:
            self.control_tab.increaseSpeedX()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Increase Speed X')
            return
        if command.code == 4:
            self.control_tab.decreaseSpeedX()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Decrease Speed X')
            return
        if command.code == 16:
            self.control_tab.rightSpeedY()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Increase Speed Y')
            return
        if command.code == 15:
            self.control_tab.leftSpeedY()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Decrease Speed Y')
            return
        if command.code == 12:
            self.control_tab.stopSpeedXY()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Stop Horizontal Movement')
            return
        if command.code == 13:
            self.control_tab.stopSpeedZ()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Stop Vertical Movement')
            return
        if command.code == 14:
            self.state = "ON MISSION"
            self.control_tab.activateMission(command.data)
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Activate Mission')
            return
        if command.code == 6:
            self.state = "MISSION CANCEL"
            self.control_tab.cancelMission()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Cancel Mission')
            self.freeze()
            return
        if command.code == 17:
            self.state = "MOTORS KILL"
            self.control_tab.killMotorsNow()
            logging.debug('Executing Code: %s for Command: %s', str(command.code), 'Emergency Motor Kill')
            self.is_active = False
