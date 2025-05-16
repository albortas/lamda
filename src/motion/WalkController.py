import numpy as np
from math import sin, cos

from src.cmass.CenterMass import CenterMass
from src.kinematics.kinematics import inverse_kinematics_all
from src.utils.transformations import xyz_rotation_matrix, new_coordinates
from src.motion.UpdateMovement import UpdateMovement
from src.motion.CrawlController import CrawlController


class WalkGaitController():       
    def __init__(self, x_offset, default_height, legs, default_stance, default_frame):
        self.legs = legs
        self.CG = np.zeros(3)
        self.centerMass = CenterMass(default_frame, legs)
        self.updateMovement = UpdateMovement(default_stance)
        self.crawlController = CrawlController(x_offset, default_height, self.CG, default_stance, default_frame)
        
    def updateStateCommand(self, msg, state, command):
        command.velocity = [msg.axes[1], msg.axes[0]]
        command.yaw_rate = msg.axes[3]
        
    def step(self, state):
        xc, yc = self.crawlController.steering_center(state)
        state.center = [state.center_map[0]+(xc*cos(state.theta[2])-yc*sin(state.theta[2])),
                        state.center_map[1]+(xc*sin(state.theta[2])+yc*cos(state.theta[2]))]
        state.angles_foot = inverse_kinematics_all(state.foot_position,self.legs)
        self.CG = self.centerMass.CM_calculation_o(state.angles_foot)
        M = xyz_rotation_matrix(state.theta[0], state.theta[1], state.theta[2])
        state.CGabs = new_coordinates(M, self.CG[0], self.CG[1], self.CG[2],
                                      state.framecenter_comp[0], state.framecenter_comp[1], state.framecenter_comp[2])
        state.dCG = self.centerMass.CG_distance(state.foot_abs[0], state.foot_abs[1], state.foot_abs[2], state.CGabs[0], state.CGabs[1], state.stance)
        
    def run(self, state, command):
        self.step(state)
        if command.walking:
            state.t += 0.01
            state.t1 = state.t % 1
            self.updateMovement.update_movement(state, command)
            self.crawlController.start_walk_stop(state)
        
    
        
        
        