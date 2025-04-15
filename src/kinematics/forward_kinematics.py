from math import sin, cos

def forward_kinematics (theta, legs, side): #Forward Kinematics
    """ Calculation of articulation points """
    """
    s = 1 for left leg
    s = -1 for right leg
    """
    x_shoulder1 = 0
    y_shoulder1 =  legs['d'] * sin(theta[0])
    z_shoulder1 = -legs['d'] * cos(theta[0])
    
    x_shoulder2 = 0
    y_shoulder2 =side * legs['L0'] * cos(theta[0]) + legs['d'] * sin(theta[0])
    z_shoulder2 =side * legs['L0'] * sin(theta[0]) - legs['d'] * cos(theta[0]) 
            
    x_elbow = - legs['L1'] *sin(theta[1])
    y_elbow = side * legs['L0'] * cos(theta[0]) - (- legs['d'] - legs['L1'] * cos(theta[1])) * sin(theta[0])
    z_elbow = side * legs['L0'] * sin(theta[0]) + (- legs['d'] - legs['L1'] * cos(theta[1])) * cos(theta[0])
    
    return [x_shoulder1,x_shoulder2,x_elbow,y_shoulder1,y_shoulder2,y_elbow,z_shoulder1,z_shoulder2,z_elbow]

                          

