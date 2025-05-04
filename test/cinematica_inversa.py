from math import sqrt, asin, acos, pi, sin, sin
d = 10.73
L0 = 58.09
L1 = 108.31
L2 = 138.00
x = 0.5
y = 10
z = 200
side = 1

def IK1 (): #Inverse Kinematics
    """
        s = 1 for left leg
        s = -1 for right leg
    """
    
    t2 = y**2
    t3 = z**2
    t4 = t2+t3
    t5 = 1/sqrt(t4)
    t6 = L0**2
    t7 = t2+t3-t6
    t8 = sqrt(t7)
    t9 = d-t8
    t10 = x**2
    t11 = t9**2
    t15 = L1**2
    t16 = L2**2
    t12 = t10+t11-t15-t16
    t13 = t10+t11
    t14 = 1/sqrt(t13)
    try:
        theta1 = side*(-pi/2+asin(t5*t8))+asin(t5*y)
        aux1 = -asin(t14*x)
        aux2 = asin(L2*t14*sqrt(1/t15*1/t16*t12**2*(-1/4)+1))
        theta2= aux1 + aux2
        theta3 =-pi + acos(-t12/2/(L1*L2))
        print(aux2)
    
    
    except ValueError:
        print ('ValueError IK')
        theta1=90
        theta2=90
        theta3=90
    
    theta = [theta1, theta2, theta3]
    print("IK1: ",theta)
    
def IK2 (): #Inverse Kinematics
    """
    s = 1 for left leg
    s = -1 for right leg
    """
    C = sqrt(y**2 + z**2)
    E = sqrt(C**2 - L0**2)
    D = E - d
    G = sqrt(x**2 + D**2)
    try:
        alpha = asin(E / C)
        beta = asin(y / C)
        theta1 = side * (-pi/2 + alpha) + beta
        theta3 = acos((L1**2 + L2**2 - G**2)/(2 * L1 * L2))
        gamma = -asin(x/G)
        sigma = acos((L1**2 + G**2 - L2**2)/(2 * L1 * G))
        theta2 = gamma + sigma
        
    except ValueError:
        print ('ValueError IK')
        theta1=90
        theta2=90
        theta3=90
    
    theta = [theta1, theta2, theta3]
    print("IK2: ",theta)
    
if __name__ == '__main__':
    IK1()
    IK2()