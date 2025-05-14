from math import sin,cos,pi


"""Inertia Centers"""
    
""" Body"""
xCG_Body = 0
yCG_Body = 0
zCG_Body = 0
Weight_Body = 897

""" Left Shoulder """
xCG_Shoulder = 0
yCG_Shoulder = 5 #minus for right leg
zCG_Shoulder = -9
Weight_Shoulder = 99.3

""" Left Leg """
xCG_Leg = 0
yCG_Leg = 0 #minus for right leg
zCG_Leg = -31
Weight_Leg = 133.3

""" Left Leg """
xCG_Foreleg = 0
yCG_Foreleg = 0 #minus for right leg
zCG_Foreleg = -28
Weight_Foreleg = 107

L0 = 58.09 #Shoulder articulation width
d = 10.73 #Shoulder articulation height
L1 = 108.31 #Leg length

def FK_Weight (theta, side): #Forward Kinematics for calculation of Center of Gravity
    """ Calculation of articulation points """
    """
    side = 1 for left leg
    side = -1 for right leg
    """
            
    xCG_Shoulder1 = xCG_Shoulder
    yCG_Shoulder1 = side * yCG_Shoulder * cos(theta[0]) - zCG_Shoulder*sin(theta[0])
    zCG_Shoulder1 = side * yCG_Shoulder * sin(theta[0]) + zCG_Shoulder*cos(theta[0]) 
            
    xCG_Leg1 = xCG_Leg*cos(theta[1]) + zCG_Leg*sin(theta[1])
    yCG_Leg1 = cos(theta[0])*(L0 * side + side * yCG_Leg) + sin(theta[0])*(d - zCG_Leg*cos(theta[1]) + xCG_Leg*sin(theta[1]))
    zCG_Leg1 = sin(theta[0])*(L0 * side + side * yCG_Leg) - cos(theta[0])*(d - zCG_Leg*cos(theta[1]) + xCG_Leg*sin(theta[1]))
    
    xCG_Foreleg1 = cos(theta[1])*(xCG_Foreleg*cos(theta[2]) + zCG_Foreleg*sin(theta[2])) - sin(theta[1])*(L1 - zCG_Foreleg*cos(theta[2]) + xCG_Foreleg*sin(theta[2]))
    yCG_Foreleg1 = cos(theta[0])*(L0*side + side * yCG_Foreleg) + sin(theta[0])*(d + sin(theta[1])*(xCG_Foreleg*cos(theta[2]) + zCG_Foreleg*sin(theta[2])) + cos(theta[1])*(L1 - zCG_Foreleg*cos(theta[2]) + xCG_Foreleg*sin(theta[2])))
    zCG_Foreleg1 = sin(theta[0])*(L0*side + side * yCG_Foreleg) - cos(theta[0])*(d + sin(theta[1])*(xCG_Foreleg*cos(theta[2]) + zCG_Foreleg*sin(theta[2])) + cos(theta[1])*(L1 - zCG_Foreleg*cos(theta[2]) + xCG_Foreleg*sin(theta[2])))
    
    return [xCG_Shoulder1,xCG_Leg1,xCG_Foreleg1,yCG_Shoulder1,yCG_Leg1,yCG_Foreleg1,zCG_Shoulder1,zCG_Leg1,zCG_Foreleg1]

if __name__ == "__main__":
    theta = [0,0,0]
    print(FK_Weight(theta,1))