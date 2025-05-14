from math import sin, cos, sqrt
from dataclasses import dataclass

# Constants
BODY_WEIGHT = 897
SHOULDER_WEIGHT = 99.3
LEG_WEIGHT = 133.3
FORELEG_WEIGHT = 107

@dataclass
class BodyPart:
    x: float
    y: float
    z: float
    weight: float

# Body parts configuration
BODY = BodyPart(0, 0, 0, BODY_WEIGHT)
SHOULDER = BodyPart(0, 5, -9, SHOULDER_WEIGHT)
LEG = BodyPart(0, 0, -31, LEG_WEIGHT)
FORELEG = BodyPart(0, 0, -28, FORELEG_WEIGHT)

class CGravity:
    def __init__(self, default_frame, legs):
        self.default_frame = default_frame
        self.legs = legs
        
    def _transform_coordinates(self, theta, part, side, is_foreleg=False):
        """Helper method to transform coordinates based on angles"""
        if part == SHOULDER:
            x = part.x
            y = side * part.y * cos(theta[0]) - part.z * sin(theta[0])
            z = side * part.y * sin(theta[0]) + part.z * cos(theta[0])
            return x, y, z
        
        if part == LEG and not is_foreleg:
            x = part.x * cos(theta[1]) + part.z * sin(theta[1])
            y = side * (self.legs['L0'] + part.y) * cos(theta[0])+ \
                (self.legs['d'] + part.x * sin(theta[1]) - part.z * cos(theta[1])) * sin(theta[0])
            z = side * (self.legs['L0'] + part.y) * sin(theta[0]) - \
                (self.legs['d'] + part.x * sin(theta[1]) - part.z * cos(theta[1])) * cos(theta[0])
            return x, y, z
        
        if part == FORELEG or is_foreleg:
            x = -self.legs['L1'] * sin(theta[1]) + \
                part.x * cos(theta[1] + theta[2]) + part.z * cos(theta[1] + theta[2])
            y = side * (self.legs['L0'] + part.y) * cos(theta[0]) + \
                (self.legs['d'] + self.legs['L1'] * cos(theta[1]) + part.x * sin(theta[1] + theta[2]) - part.z * cos(theta[1] + theta[2])) * sin(theta[0])
            z = side * (self.legs['L0'] + part.y) * sin(theta[0]) - \
                (self.legs['d'] + self.legs['L1'] * cos(theta[1]) + part.x * sin(theta[1] + theta[2]) - part.z * cos(theta[1] + theta[2])) * cos(theta[0])
            return x, y, z
    
    def FK_Weight(self, theta, side):
        """Ciematica Directa para el cálculo del Centro de Gravedad"""
        shoulder = self._transform_coordinates(theta, SHOULDER, side)
        leg = self._transform_coordinates(theta, LEG, side)
        foreleg = self._transform_coordinates(theta, FORELEG, side, is_foreleg=True)
        print(shoulder, leg, foreleg)
        return shoulder + leg + foreleg  # Returns tuple of 9 values
           
    def CG_calculation(self,theta):
        cg_positions = {
            'lf': self.FK_Weight(theta[:,0], 1),
            'rf': self.FK_Weight(theta[:,1], -1),
            'rr': self.FK_Weight(theta[:,2], -1),
            'lr': self.FK_Weight(theta[:,3], 1)
        }
        
        total_weight = BODY.weight + 4 * (SHOULDER.weight + LEG.weight + FORELEG.weight)
                       
        # Calculate weighted positions for each axis
        def calculate_axis(axis_idx, body_part_idx, body_weight_component):
            weighted_sum = sum(
                (pos[body_part_idx] + self.default_frame[axis_idx, i]) * weight
                for i, (leg, pos) in enumerate(cg_positions.items())
                for weight, body_part_idx in [
                    (SHOULDER.weight, 0 + axis_idx*3),
                    (LEG.weight, 1 + axis_idx*3),
                    (FORELEG.weight, 2 + axis_idx*3)
                ]
            )
            return (weighted_sum + body_weight_component * BODY.weight) / total_weight
        
        x_cg = calculate_axis(0, 0, BODY.x)
        y_cg = calculate_axis(1, 1, BODY.y)
        z_cg = calculate_axis(2, 2, BODY.z)
        
        print (x_cg, y_cg, z_cg)
        
        return x_cg, y_cg, z_cg
             
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
