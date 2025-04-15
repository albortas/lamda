import numpy as np
from enum import Enum

""" class BehaviorState(Enum):
    REST = 0
    STAND = 1
    CRAWL = 2 """

class State:    #Estado actual del robot
    def __init__(self, default_stance, default_position, framecenter_comp):
        #self.robot_height = -default_height
        self.velocity = np.array([0., 0.])
        self.yaw_rate = 0.
        self.t = 0
        self.steering = 0.
        self.walking_direction = 0.
        self.walking_speed = 0.
        self.cw = 1
        self.step_phase = ""
        self.theta = np.zeros(6)
        self.body_center = np.zeros(3)
        self.center = np.zeros(2)
        self.angles_foot = np.zeros((3,4))
        self.foot_abs = default_stance
        self.foot_position = default_position
        self.framecenter_comp = framecenter_comp
        self.CGabs = np.zeros(3)
        self.dCG = [0., 0., False]
        self.stance = [True, True, True, True]
        #self.body_local_position = np.array([0., 0., 0.])
        #self.body_local_orientation = np.array([0., 0., 0.])
        #self.imu_roll = 0.
        #self.imu_pitch = 0.
        self.ticks = 0
        #self.behavior_state = BehaviorState.REST
       
class Command:  #Comandos que se envian al robot
    def __init__(self):
        #self.robot_height = -default_height
        self.velocity = np.array([0., 0.])
        self.yaw_rate = 0.
        self.lock = False
        self.stop = False
        self.free = True
        self.walking = False
        self.tstart = 0
        self.tstop = 0
        self.trec = 0
        