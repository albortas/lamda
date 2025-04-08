import numpy as np
from enum import Enum

class BehaviorState(Enum):
    REST = 0
    STAND = 1
    CRAWL = 2

class State:    #Estado actual del robot
    def __init__(self, default_height):
        self.robot_height = -default_height
        self.velocity = np.array([0., 0.])
        self.yaw_rate = 0.
        self.foot_locations = np.zeros((3,4))
        self.body_local_position = np.array([0., 0., 0.])
        self.body_local_orientation = np.array([0., 0., 0.])
        self.imu_roll = 0.
        self.imu_pitch = 0.
        self.ticks = 0
        self.behavior_state = BehaviorState.REST
       
class Command:  #Comandos que se envian al robot
    def __init__(self, default_height):
        self.robot_height = -default_height
        self.velocity = np.array([0., 0.])
        self.yaw_rate = 0.
        self.rest_event = False
        self.stand_event = False
        self.crawl_event = False
        