import numpy as np

from math import sin, cos, sqrt
from dataclasses import dataclass

# Constants
BODY_WEIGHT = 897
HIP_WEIGHT = 99.3
THIGH_WEIGHT = 133.3
FOOT_WEIGHT = 107

@dataclass
class BodyPart:
    x: float
    y: float
    z: float
    weight: float

# Body parts configuration
BODY = BodyPart(0, 0, 0, BODY_WEIGHT)
HIP = BodyPart(0, 5, -9, HIP_WEIGHT)
THIGH = BodyPart(0, 0, -31, THIGH_WEIGHT)
FOOT = BodyPart(0, 0, -28, FOOT_WEIGHT)

class CGravity:
    def __init__(self, default_frame, legs):
        self.default_frame = default_frame
        self.legs = legs
    
    def compute_leg_segments_cm(self, theta, side):
        
        x_h = HIP.x
        y_h = side * HIP.y * cos(theta[0]) - HIP.z * sin(theta[0])
        z_h = side * HIP.y * sin(theta[0]) + HIP.z * cos(theta[0])
        
        x_t = THIGH.x * cos(theta[1]) + THIGH.z * sin(theta[1])
        y_t = side * (self.legs['L0'] + THIGH.y) * cos(theta[0])+ \
            (self.legs['d'] + THIGH.x * sin(theta[1]) - THIGH.z * cos(theta[1])) * sin(theta[0])
        z_t = side * (self.legs['L0'] + THIGH.y) * sin(theta[0]) - \
            (self.legs['d'] + THIGH.x * sin(theta[1]) - THIGH.z * cos(theta[1])) * cos(theta[0])
        
        x_f = -self.legs['L1'] * sin(theta[1]) + FOOT.x * cos(theta[1] + theta[2]) + FOOT.z * sin(theta[1] + theta[2])
        y_f = side * (self.legs['L0'] + FOOT.y) * cos(theta[0]) + \
            (self.legs['d'] + self.legs['L1'] * cos(theta[1]) + FOOT.x * sin(theta[1] + theta[2]) - FOOT.z * cos(theta[1] + theta[2])) * sin(theta[0])
        z_f = side * (self.legs['L0'] + FOOT.y) * sin(theta[0]) - \
            (self.legs['d'] + self.legs['L1'] * cos(theta[1]) + FOOT.x * sin(theta[1] + theta[2]) - FOOT.z * cos(theta[1] + theta[2])) * cos(theta[0])
                
        return np.array([[x_h, x_t, x_f],
                         [y_h, y_t, y_f],
                         [z_h, z_t, z_f]])
        
    def CM_calculation_o(self,theta):
        cg_positions = [
            self.compute_leg_segments_cm(theta[:,0], 1),  # lf
            self.compute_leg_segments_cm(theta[:,1], -1), # rf
            self.compute_leg_segments_cm(theta[:,2], -1), # rr
            self.compute_leg_segments_cm(theta[:,3], 1)   # lr
        ]
        total_weight = BODY.weight + 4 * (HIP.weight + THIGH.weight + FOOT.weight)
        s_cg = np.zeros((3,4))
               
        for i in range(4):
            s_cg[:,i] = (cg_positions[i] + self.default_frame[:,i, np.newaxis]) @ np.array([HIP.weight,THIGH.weight,FOOT.weight])
        
        cm = np.sum(s_cg, axis=1) + np.array([BODY.x,BODY.y,BODY.z])*BODY.weight
        return cm / total_weight
        
             
    def CG_distance (self,x_legs,y_legs,z_legs,xcg,ycg,stance):
        
        # line equation c * x + s * y - p  = 0
        # with c = a/m et s = b/m
         
        a1 = (y_legs[0]-y_legs[2])
        b1 = -(x_legs[0]-x_legs[2])
        m1 =sqrt(a1**2 + b1**2)
        c1 = a1/m1
        s1 = b1/m1
        
        a2 = (y_legs[1]-y_legs[3])
        b2 = -(x_legs[1]-x_legs[3])
        m2 =sqrt(a2**2 + b2**2)
        c2 = a2/m2
        s2 = b2/m2   
        
        p1 = c1*x_legs[0] + s1*y_legs[0]
        p2 = c2*x_legs[1] + s2*y_legs[1]
        
        """ Dstance calculation """
        d1 = c1*xcg + s1*ycg - p1
        d2 = c2*xcg + s2*ycg - p2
        
        """ intersection calculation """
        #perpendicalar line equation -s * x + c * y - q = 0
        
        q1 = -s1*xcg +c1*ycg
        q2 = -s2*xcg +c2*ycg
        
        xint1 = c1*p1 - s1*q1
        yint1 = c1*q1 + s1*p1
        
        xint2 = c2*p2 - s2*q2
        yint2 = c2*q2 + s2*p2
        
        """ Check if inside sustentation triangle """
        d = 0
        xint = xcg
        yint = ycg
        if (stance[0]== False)|(stance[2]== False): 
            d = d2
            xint = xint2
            yint = yint2
            
        
        if (stance[1]== False)|(stance[3]== False): 
            d = d1
            xint = xint1
            yint = yint1  
            
        balance = True
    
        if (stance[0] == False)&(d< 0):
            balance = False
            
        if (stance[1] == False)&(d> 0):
            balance = False    
        
        if (stance[2] == False)&(d> 0):
            balance = False    
            
        if (stance[3] == False)&(d< 0):
            balance = False  
            
        if (balance == False):
            d=-abs(d)
        else:
            d=abs(d)
        
        return xint, yint, balance
    

