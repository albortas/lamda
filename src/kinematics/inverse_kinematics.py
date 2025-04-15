import numpy as np
from math import sqrt, asin, acos, pi

def inverse_kinematics(x, y, z, legs, side):
    """Calulo de cinematica de inversa
       s = 1 for left leg (pierna izquierda)
       s = -1 for right leg (pierna derecha)"""
    
    t2 = y**2
    t3 = z**2
    t4 = t2+t3
    t5 = 1/sqrt(t4)
    t6 = legs['L0']**2
    t7 = t2+t3-t6
    t8 = sqrt(t7)
    t9 = legs['d']-t8
    t10 = x**2
    t11 = t9**2
    t15 = legs['L1']**2
    t16 = legs['L2']**2
    t12 = t10+t11-t15-t16
    t13 = t10+t11
    t14 = 1/sqrt(t13)
    try:
        theta1 = side*(-pi/2+asin(t5*t8))+asin(t5*y)
        theta2= -asin(t14*x)+asin(legs['L2']*t14*sqrt(1/t15*1/t16*t12**2*(-1/4)+1))
        theta3 =-pi + acos(-t12/2/(legs['L1']*legs['L2']))
        
    except ValueError:
        print ('ValueError IK')
        theta1=90
        theta2=90
        theta3=90
    
    theta = [theta1, theta2, theta3]
    return theta

def inverse_kinematics_all(pos_init, legs):
    #LF, RF, RR, LR
    foot = [1, -1, -1, 1]
    angles = np.zeros((3,4))    
    for i in range(4):
        x = pos_init[0,i]
        y = pos_init[1,i]
        z = pos_init[2,i]
        angles[:,i] = inverse_kinematics(x, y, z, legs, foot[i])
    return angles
        