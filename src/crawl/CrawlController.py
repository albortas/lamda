import numpy as np
from time import sleep
from math import pi, cos, sin, sqrt, atan2

""" Walking parameters """
h_amp = 100
coef = 1.2

class SteeringUpdate:
    def __init__(self, state, command):
        self.module = 0
        self.cw = 0
        self.steering = state.steering
        self.walking_direction = state.walking_direction
        self.walking_speed = state.walking_speed
        self.velocity = command.velocity
        self.yaw_rate = command.yaw_rate
        self.yaw_inv = command.yaw_inv
        
    
    def swing_update_direction(self, state, command):
        if abs(command.velocity[0]) > 0.2 or abs(command.velocity[1]) > 0.2 or command.stop:
            command.trec = int(state.t) + 1
        
            module_old = self.module
            walking_direction_old = self.walking_direction
            
            x_old = module_old*cos(walking_direction_old)
            y_old = module_old*sin(walking_direction_old)
            
            #update request
            self.module = sqrt(command.velocity[0]**2 + command.velocity[1]**2)
            self.walking_direction = (atan2(-command.velocity[1],-command.velocity[0])%(2*pi)+pi/2)%(2*pi)
            
            x_new = self.module*cos(self.walking_direction)
            y_new = self.module*sin(self.walking_direction)
            
            self.swing_update_steering(command)
            
            gap = sqrt((x_new-x_old)**2+(y_new-y_old)**2)
            
            if (gap > 0.01):
                x_new = x_old+ (x_new-x_old)/gap*0.01
                y_new = y_old+ (y_new-y_old)/gap*0.01
                self.module = sqrt(x_new**2+y_new**2)
                state.walking_direction = atan2(y_new,x_new)
                                                    
            #reduces speed sideways and backwards  
            min_h_amp = h_amp*(1/2e6* state.steering+1/2)               
            xa = 1+cos(state.walking_direction-pi/2) 
            state.walking_speed = min (1, self.module) * min(h_amp,min_h_amp) * (1/8*xa**2+1/8*xa+1/4)
            
    def swing_update_steering(self, command):
        """steering update"""
        steering_old = self.steering
        if (abs(command.yaw_rate) < 0.2):
            self.cw = 1
            if (self.steering<2000):
                self.steering = min(1e6,steering_old*coef) 
            else:
                self.steering = 1e6
        else:
            self.steering = 2000-(abs(command.yaw_inv)-0.2)*2000/0.8+0.001
            if ((self.steering/steering_old)>coef):                       
                self.steering = steering_old*coef
            if ((steering_old/self.steering)>coef):                       
                self.steering = steering_old/coef   
                if (self.steering <0.001):
                    self.steering = 0.001
            self.cw = -np.sign(command.yaw_inv)
    
    def stance_update_direction(self, state, command):
        if abs(command.velocity[0]) < 0.2 and abs(command.velocity[1]) < 0.2 and not command.stop:
            self.module = max (0, self.module - 0.01)
            self.walking_speed = self.module* h_amp * ((1+cos(self.walking_direction-pi/2))/2*0.75+0.25)
            if (self.steering<2000):
                self.steering = min(1e6,state.steering*coef) 
            else:
                self.steering = 1e6
            self.cw = 1
            if (state.t > command.trec):
                state.t = command.trec
                
    def steering_update(self, state, command):
        self.swing_update_direction(state, command)
        self.stance_update_direction(state, command)
        return self.steering, self.walking_direction, self.walking_speed
    
    
    
    
    
    
                
    @property
    def coor_circle(self):
        x = self.steering * np.cos(self.walking_direction)
        y = self.steering * np.sin(self.walking_direction)
        return x, y
    
    @property
    def foot_position(self):
        return self.default_stance[0], self.default_stance[1]
    
    @property
    def nominal_radius_angle(self):
        radii = np.sqrt((self.coor_circle[0]-self.foot_position[0])**2 + (self.coor_circle[1]-self.foot_position[1])**2)
        an = np.arctan2(self.foot_position[1] - self.coor_circle[1], self.foot_position[0] - self.coor_circle[0])
        return radii, an
    
    @property
    def mangle(self):
        maxr = max(self.nominal_radius_angle[0])
        return self.walking_speed/maxr
    
    def dtheta(self, step_phase):
        stepl = 0.125
        if (step_phase =='start')|(step_phase == 'stop'):           
            dtheta = self.mangle/(1-stepl)*0.01/2*self.cw
        else:
            dtheta = self.mangle/(1-stepl)*0.01*self.cw
        return dtheta
    
