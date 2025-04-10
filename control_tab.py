import time, logging
from dronekit import VehicleMode, Command
from engine import Engine
from pymavlink import mavutil
from path_planner import PathPlanner
import subprocess, socket
import os
import signal

class ControlTab:
    def __init__(self, drone):
        self.vehicle = drone.vehicle
        self.drone = drone
        
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.increment_value_x = 0.5
        self.increment_value_y = 0.5
        self.increment_value_z = 0.2
        self.rotation_angle = 10
        self.engine = Engine(drone, self)
        self.engine.start()
        self.obstacle_process = None
        
    def stopMovement(self):
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.engine.executeChangesNow()
        
    def rotateLeft(self, angle):
        self.engine.rotate(-1, angle)
    
    def rotateRight(self, angle):
        self.engine.rotate(1, angle)
        
    def increaseSpeedX(self):
        self.speed_x = self.speed_x + self.increment_value_x
        self.engine.executeChangesNow()
        
    def decreaseSpeedX(self):
        self.speed_x = self.speed_x - self.increment_value_x
        self.engine.executeChangesNow()
   
    def leftSpeedY(self):
        self.speed_y = self.speed_y - self.increment_value_y
        self.engine.executeChangesNow()
        
    def rightSpeedY(self):
        self.speed_y = self.speed_y + self.increment_value_y
        self.engine.executeChangesNow()
        
    def stopSpeedXY(self):
        self.speed_x = 0
        self.speed_y = 0
        self.engine.executeChangesNow()
        
    def increaseSpeedZ(self):
        self.speed_z = self.speed_z - self.increment_value_z
        self.engine.executeChangesNow()
        
    def decreaseSpeedZ(self):
        self.speed_z = self.speed_z + self.increment_value_z
        self.engine.executeChangesNow()
        
    def stopSpeedZ(self):
        self.speed_z = 0
        self.engine.executeChangesNow()
        
    def killMotorsNow(self):
        self.engine.killMotorsNow()
        
    def armAndTakeoff(self, takeoff_alt):
        logging.info("Arming") 
        
        self.vehicle.mode = VehicleMode("GUIDED")   

        self.vehicle.armed = True
        time.sleep(1)
    
        count = 10
        while not self.vehicle.armed and count > 0:
            logging.debug('self.vehicle.armed: ' + str(self.vehicle.armed))
            self.vehicle.armed = True
            count -= 1  # Decrement the count
            time.sleep(1)
        
        self.vehicle.simple_takeoff(takeoff_alt)
        logging.info("Takeoff")

        while True:
            current_hight = self.vehicle.location.global_relative_frame.alt
        
            if current_hight >= takeoff_alt * 0.95:
                logging.info("Altitude reached")
                #commanding movement to the same location to unlock Yaw
                self.vehicle.simple_goto( self.vehicle.location.global_relative_frame)
                break
            time.sleep(1)
        
    def goHome(self, rtl_alt):
        logging.info('Going Home')
        self.vehicle.mode = VehicleMode("GUIDED")

        for _ in range(0,10):
            self.increaseSpeedZ()
            time.sleep(0.5)
        
        while True:
            current_hight = self.vehicle.location.global_relative_frame.alt
        
            if current_hight >= rtl_alt * 0.95:
                logging.info("Safe RTL Altitude reached")
                self.vehicle.mode = VehicleMode("RTL")
                break
            time.sleep(1)
	
    def cancelMission(self):
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.commands.next = 0
        self.engine.lastMissionCmndIndex = -1
        cmds = self.vehicle.commands
        cmds.clear()
        cmds.upload()

        if self.obstacle_process is not None:
            os.kill(self.obstacle_process.pid, signal.SIGTERM)  # Kill process
            self.obstacle_process = None
        
    def activateMission(self, command_data):
        if self.vehicle.mode == VehicleMode("AUTO"):
            self.vehicle.mode = VehicleMode("GUIDED")
            self.drone.state = "MISSION PAUSE"
            self.drone.freeze()
            return
        
        if self.vehicle.commands.next > 0 and self.vehicle.mode == VehicleMode("GUIDED"):
            self.drone.state = "MISSION RESUME"
            self.vehicle.mode = VehicleMode("AUTO")
            return
        
        self.vehicle.commands.next = 0
        cmds = self.vehicle.commands
        cmds.clear()
        # add & remove command because of the bug(not seeing first time added command)
        cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                          mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 
                          float(0), float(0), float(0)  ))
        cmds.clear()
        
        if not self.vehicle.armed:
            self.armAndTakeoff( self.drone.takeoff_alt)

        """ Uses path planner to generate a mission path and starts execution. """
        points_data = [(float(point.longitude), float(point.latitude)) for point in command_data.point]
        boundary = PathPlanner.construct_boundary(points_data)
        path = PathPlanner.boustrophedon_coverage(boundary)
        
        if not path:
            logging.error("Path planning failed!")
            return
        
        start = path[0]
        goal = path[-1]
        obstacles = set()

        points_data = {"point": [{"latitude": lat, "longitude": lon, "altitude": 10} for lat, lon in path]}
        
        for point in points_data["point"]:
            cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                             mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 
                             float(point["latitude"]), float(point["longitude"]), float(point["altitude"])))
        
        #add dummy waypoint (to let us know we have reached the destination)
        cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                          mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 
                          float(0), float(0), float(0)  ))
        
        self.engine.lastMissionCmndIndex = cmds.count
        cmds.upload()
        
        self.vehicle.mode = VehicleMode("AUTO")

        if obstacle_process is None:
            obstacle_process = subprocess.Popen(["python3", "obstacle_detection.py"])

        # Connect to the obstacle detection service
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.bind(("127.0.0.1", 5005))

        # Iterate through the points in points_data to move the drone
        for point in points_data["point"]:
            # Send waypoint command to the drone (using MAVLink, already done above)

            # Check for obstacle detection
            client.settimeout(0.1)  # Timeout after 100ms
            try:
                data, _ = client.recvfrom(1024)
                if data.decode() == "OBSTACLE":
                    print("Obstacle detected! Recalculating path...")

                    # Stop drone at current position (stay at the current point)
                    current_lat = self.vehicle.location.global_relative_frame.lat
                    current_lon = self.vehicle.location.global_relative_frame.lon
                    current_alt = self.vehicle.location.global_relative_frame.alt
                    self.vehicle.simple_goto(current_lat, current_lon, current_alt)  # Drone stays stationary

                    obstacles = set([(current_lat, current_lon)])  # Add current position as obstacle
                    new_path = PathPlanner.a_star(start, goal, obstacles)  # Recalculate path using A* (lat/lon)
                    if new_path:
                        path = new_path  # Update the path

                        # Convert new path to points_data for drone commands
                        points_data = {"point": [{"latitude": lat, "longitude": lon, "altitude": 10} for lat, lon in path]}

                        # Re-send commands based on the new path
                        cmds.clear()  # Clear previous commands
                        for point in points_data["point"]:
                            cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                                             mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 
                                             float(point["latitude"]), float(point["longitude"]), float(point["altitude"])))
                        cmds.upload()

            except socket.timeout:
                pass  # No obstacle detected, continue with the current path
            
            # Send current point's command to the drone (execute movement)
            print(f"Moving to {point['latitude']}, {point['longitude']}")
            time.sleep(1)  # Simulate drone movement (adjust this for real drone movement)
        
    def land(self):
        logging.info("Landing")
        self.vehicle.channels.overrides = {}
        self.vehicle.mode = VehicleMode("LAND")

