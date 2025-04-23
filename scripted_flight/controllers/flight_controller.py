import time
import numpy as np
from enum import Enum
from scripted_flight.controllers.vicon_flow_utils import get_position

# Simple 1D Kalman Filter for altitude smoothing.
class SimpleKalmanFilter:
    def __init__(self, process_variance=0.01, measurement_variance=0.1, initial_estimate=0.0):
        self.x = initial_estimate
        self.P = 1.0
        self.Q = process_variance
        self.R = measurement_variance

    def update(self, measurement):
        self.P += self.Q
        K = self.P / (self.P + self.R)
        self.x += K * (measurement - self.x)
        self.P *= (1 - K)
        return self.x

class FlightState(Enum):
    IDLE = 0
    TAKEOFF = 1
    DEMO = 2
    HOVER = 3
    LAND = 4
    DONE = 5

class FlightController:
    def __init__(self, cf, vicon, marker, params, pattern=None):
        self.cf = cf
        self.vicon = vicon
        self.marker = marker
        self.params = params
        self.pattern = pattern  # Optional demo/formation pattern function.
        self.state = FlightState.IDLE
        self.desired = np.zeros(3)
        self.alt_filter = SimpleKalmanFilter(initial_estimate=0.0)

    def run(self):
        kp_xy    = self.params.get('kp_xy', 0.2)
        kp_z     = self.params.get('kp_z', 1.0)
        takeoff  = self.params.get('takeoff_height', 1.0)
        demo_dur = self.params.get('demo_duration', 20)
        hover_dur= self.params.get('hover_duration', 10)
        land_thresh = self.params.get('land_thresh', 0.1)
        db_xy    = self.params.get('deadband_xy', 0.005)
        db_z     = self.params.get('deadband_z', 0.005)
        max_vel_xy = self.params.get('max_vel_xy', 0.25)
        max_vel_z  = self.params.get('max_vel_z', 0.6)
        rate     = self.params.get('control_rate', 100)
        zrange   = self.params.get('zrange')
        
        # PHASE 1: TAKEOFF
        while self.state in (FlightState.IDLE, FlightState.TAKEOFF):
            pos, occluded = get_position(self.vicon, self.marker)
            if occluded or pos is None:
                time.sleep(1.0 / rate)
                continue
            filtered_alt = self.alt_filter.update(zrange[0] / 1000.0)
            if self.state == FlightState.IDLE:
                self.desired = pos.copy()
                self.desired[2] = takeoff
                self.state = FlightState.TAKEOFF
            elif self.state == FlightState.TAKEOFF:
                if abs(self.desired[2] - filtered_alt) <= land_thresh:
                    # If a pattern is provided (e.g., dynamic formation), enter DEMO;
                    # otherwise, enter HOVER mode.
                    self.state = FlightState.DEMO if self.pattern else FlightState.HOVER
                    phase_start = time.time()
            self._avoid_obstacles()
            self._send_command(pos, filtered_alt, kp_xy, kp_z, db_xy, db_z, max_vel_xy, max_vel_z, rate)
        
        # PHASE 2: DEMO or HOVER (dynamic formation changes)
        if self.state == FlightState.DEMO:
            while time.time() - phase_start < demo_dur:
                pos, occluded = get_position(self.vicon, self.marker)
                if occluded or pos is None:
                    time.sleep(1.0 / rate)
                    continue
                filtered_alt = self.alt_filter.update(zrange[0] / 1000.0)
                now = time.time()
                self.desired = self.pattern(self, pos, filtered_alt, now)
                self._avoid_obstacles()
                self._send_command(pos, filtered_alt, kp_xy, kp_z, db_xy, db_z, max_vel_xy, max_vel_z, rate)
        elif self.state == FlightState.HOVER:
            while time.time() - phase_start < hover_dur:
                pos, occluded = get_position(self.vicon, self.marker)
                if occluded or pos is None:
                    time.sleep(1.0 / rate)
                    continue
                filtered_alt = self.alt_filter.update(zrange[0] / 1000.0)
                self._avoid_obstacles()
                self._send_command(pos, filtered_alt, kp_xy, kp_z, db_xy, db_z, max_vel_xy, max_vel_z, rate)
        
        # PHASE 3: LAND
        self.desired[2] = 0.0
        while True:
            pos, occluded = get_position(self.vicon, self.marker)
            if occluded or pos is None:
                time.sleep(1.0 / rate)
                continue
            filtered_alt = self.alt_filter.update(zrange[0] / 1000.0)
            self._send_command(pos, filtered_alt, kp_xy, kp_z, db_xy, db_z, max_vel_xy, max_vel_z, rate)
            if abs(filtered_alt - 0.0) <= land_thresh:
                break
        self.cf.commander.send_stop_setpoint()

    def _avoid_obstacles(self):
        obstacles = self.params.get("obstacle_markers", [])
        thresh = self.params.get("obstacle_threshold", 0.5)
        warp_dist = self.params.get("warp_distance", 0.3)
        for obst in obstacles:
            obst_pos, occluded = get_position(self.vicon, obst)
            if occluded or obst_pos is None:
                continue
            if np.linalg.norm(self.desired - obst_pos) < thresh:
                direction = self.desired - obst_pos
                norm = np.linalg.norm(direction)
                direction = direction / norm if norm else np.array([1, 0, 0])
                self.desired = obst_pos + direction * warp_dist

    def _send_command(self, pos, filtered_alt, kp_xy, kp_z, db_xy, db_z, max_vel_xy, max_vel_z, rate):
        error = self.desired - pos
        error[2] = self.desired[2] - filtered_alt
        error[0] = 0 if abs(error[0]) < db_xy else error[0]
        error[1] = 0 if abs(error[1]) < db_xy else error[1]
        error[2] = 0 if abs(error[2]) < db_z else error[2]
        vel = np.array([kp_xy * error[0], kp_xy * error[1], kp_z * error[2]])
        vel[0] = np.clip(vel[0], -max_vel_xy, max_vel_xy)
        vel[1] = np.clip(vel[1], -max_vel_xy, max_vel_xy)
        vel[2] = np.clip(vel[2], -max_vel_z, max_vel_z)
        self.cf.commander.send_velocity_world_setpoint(vel[0], vel[1], vel[2], 0.0)
        time.sleep(1.0 / rate)
